"""Benchmark exact N-Queens solvers, with an independent process deadline."""
import argparse
import csv
import importlib
from importlib.metadata import version, PackageNotFoundError
import json
import multiprocessing as mp
import platform
from pathlib import Path
from time import perf_counter
from comparison_solvers import METHODS as COMPARISONS, solve_n_queens, validate_board

SAT_METHODS = {'Sequential': 'sequential', 'Binomial': 'binomial', 'Binary': 'binary', 'Commander': 'commander', 'Product': 'product'}
METHODS = [*SAT_METHODS, *COMPARISONS]

class ClauseList(list):
    # Count each emitted clause once, without changing the encoding order.
    def __init__(self, primary_variables):
        super().__init__()
        self.primary_variables = primary_variables
        self.auxiliary_clauses = 0

    def append(self, clause):
        self.auxiliary_clauses += any(abs(v) > self.primary_variables for v in clause)
        super().append(clause)


def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]


def generate_clauses(n, variables, module, method):
    clauses = ClauseList(n*n)
    state = [] if method == 'Binary' else {'new_vars': 0}

    def add(group, exactly=False):
        encode = module.exactly_one if exactly else module.at_most_one
        if method == 'Binomial':
            encode(clauses, group)
        elif method == 'Binary':
            encode(clauses, state, group, n)
        else:
            encode(clauses, group, state, n)

    # Each row and column must contain exactly one queen.
    for row in variables:
        add(row, exactly=True)
    for col in range(n):
        add([variables[row][col] for row in range(n)], exactly=True)

    # Preserve the original pairwise clause order for reproducible solving.
    if method == 'Binomial':
        for i in range(n):
            for j in range(n):
                for k in range(1, n):
                    if i + k < n and j + k < n:
                        add([variables[i][j], variables[i + k][j + k]])
                    if i + k < n and j - k >= 0:
                        add([variables[i][j], variables[i + k][j - k]])
        return clauses, 0

    # Diagonals only need at-most-one; empty diagonals are allowed.
    for i in range(1, n):
        add([variables[i-k][k] for k in range(n) if 0 <= i-k < n])
    for j in range(1, n - 1):
        add([variables[n-1-k][j+k] for k in range(n) if j+k < n])
    for i in range(n - 1):
        add([variables[i+k][k] for k in range(n) if i+k < n])
    for j in range(1, n - 1):
        add([variables[k][j+k] for k in range(n) if j+k < n])
    return clauses, len(state) if method == 'Binary' else state['new_vars']


def worker(connection, n, method, limit, threads):
    stats = {}
    try:
        if method in SAT_METHODS:
            module = importlib.import_module(SAT_METHODS[method])
            from pysat.solvers import Glucose3
            start = perf_counter()
            variables = generate_variables(n)
            clauses, extra = generate_clauses(n, variables, module, method)
            stats = dict(primary_variables=n*n, auxiliary_variables=extra,
                         total_variables=n*n+extra, total_clauses=len(clauses),
                         auxiliary_clauses=clauses.auxiliary_clauses,
                         primary_only_clauses=len(clauses)-clauses.auxiliary_clauses,
                         variables=n*n+extra, clauses=len(clauses), counts_complete=True)
            connection.send({'event': 'progress', **stats})
            with Glucose3(bootstrap_with=clauses) as solver:
                built = perf_counter()
                connection.send({'event': 'progress', 'build_time': built-start})
                sat = solver.solve()
                solved = perf_counter()
                positive = {v for v in solver.get_model() if v > 0} if sat else set()
                board = [[int(variables[i][j] in positive) for j in range(n)] for i in range(n)] if sat else None
            result = dict(status='SAT' if sat else 'UNSAT', solution=board, variables=n*n+extra, clauses=len(clauses), build_time=built-start, solve_time=solved-built, total_time=solved-start, detail='Glucose3')
        else:
            result = solve_n_queens(n, method, limit, threads)
        result['valid'] = validate_board(result['solution'], n) if result['status'] == 'SAT' else None
        if result['status'] == 'SAT' and not result['valid']:
            result.update(status='ERROR', detail='Invalid N-Queens solution')
        result.pop('solution', None)
    except (ImportError, FileNotFoundError) as error:
        result = dict(status='UNAVAILABLE', detail=str(error))
    except Exception as error:
        result = dict(status='ERROR', detail=f'{type(error).__name__}: {error}')
    connection.send({'event': 'result', **stats, **result})
    connection.close()

def run_one(n, method, limit, threads):
    # A separate process lets us stop a solver even while native code is running.
    context = mp.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(sender, n, method, limit, threads))
    start = perf_counter()
    process.start()
    sender.close()
    progress = {'counts_complete': False} if method in SAT_METHODS else {}
    deadline = start + limit
    try:
        while True:
            remaining = deadline - perf_counter()
            if remaining <= 0 or not receiver.poll(max(0, remaining)):
                result = dict(progress, status='TIMEOUT', detail='Process wall-time limit reached')
                break
            try:
                message = receiver.recv()
            except EOFError:
                result = dict(progress, status='ERROR', detail='Worker exited without a result')
                break
            if message.pop('event') == 'progress':
                progress.update(message)
            else:
                result = {**progress, **message}
                break
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()
            process.join(timeout=2)
        receiver.close()
    result['wall_time'] = perf_counter()-start
    return result

def run_benchmark(args):
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = dict(python=platform.python_version(), platform=platform.platform(), processor=platform.processor(), sizes=args.sizes, methods=args.methods, timeout=args.timeout, threads=args.threads, repeats=args.repeats, timing='wall_time includes startup/imports/model/solve/cleanup; total_time excludes process startup; build_time includes solver initialization')
    metadata['counting'] = 'Counts collected from actual emitted CNF during build; counting overhead included in build_time. Missing means generation did not finish. auxiliary_clauses contains at least one auxiliary literal.'
    metadata['packages'] = {}
    for package in ['python-sat', 'ortools', 'docplex', 'cplex', 'gurobipy']:
        try:
            metadata['packages'][package] = version(package)
        except PackageNotFoundError:
            metadata['packages'][package] = None
    output.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    fields = ['N', 'Method', 'Repeat', 'status', 'wall_time', 'build_time', 'solve_time', 'total_time', 'variables', 'clauses', 'constraints', 'primary_variables', 'auxiliary_variables', 'total_variables', 'total_clauses', 'auxiliary_clauses', 'primary_only_clauses', 'counts_complete', 'valid', 'detail']
    with output.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        stream.flush()
        for n in args.sizes:
            for method in args.methods:
                for repeat in range(1, args.repeats+1):
                    result = run_one(n, method, args.timeout, args.threads)
                    writer.writerow(dict(N=n, Method=method, Repeat=repeat, **result))
                    # Keep completed runs on disk if the benchmark is interrupted.
                    stream.flush()
                    print(f"N={n:<4} {method:<12} {result['status']:<11} {result['wall_time']:.4f}s {result.get('detail', '')}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sizes', nargs='+', type=int, default=[4,8,16,32,64,128,256,512])
    parser.add_argument('--methods', nargs='+', choices=METHODS, default=METHODS)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--output', default='results/benchmark.csv')
    args = parser.parse_args()
    if min(args.sizes) < 1 or args.timeout <= 0 or args.threads < 1 or args.repeats < 1:
        parser.error('sizes, timeout, threads and repeats must be positive')
    run_benchmark(args)
