import os
from time import perf_counter
import shutil

METHODS = ['CP-SAT', 'CPLEX-CP', 'CPLEX-MIP', 'Gurobi-MIP']

def validate_board(board, n):
    if board is None or len(board) != n or any(len(row) != n or any(v not in (0, 1) for v in row) for row in board):
        return False
    cells = [(i, j) for i in range(n) for j in range(n) if board[i][j]]
    return len(cells) == n and all(len(values) == n for values in ({i for i,j in cells}, {j for i,j in cells}, {i-j for i,j in cells}, {i+j for i,j in cells}))

def diagonals(n):
    for d in range(1-n, n):
        cells = [(i, i-d) for i in range(n) if 0 <= i-d < n]
        if len(cells) > 1:
            yield cells
    for d in range(2*n-1):
        cells = [(i, d-i) for i in range(n) if 0 <= d-i < n]
        if len(cells) > 1:
            yield cells

def solve_n_queens(n, method, time_limit=60, threads=1):
    if type(n) is not int or n < 1:
        raise ValueError('n must be a positive integer')
    start = perf_counter()
    board = None
    if method == 'CP-SAT':
        from ortools.sat.python import cp_model
        model = cp_model.CpModel()
        q = [model.new_int_var(0, n-1, f'q_{i}') for i in range(n)]
        model.add_all_different(q)
        model.add_all_different([q[i]+i for i in range(n)])
        model.add_all_different([q[i]-i for i in range(n)])
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = threads
        solver.parameters.random_seed = 0
        variables, constraints = n, 3
        built = perf_counter()
        code = solver.solve(model)
        detail = solver.status_name(code)
        status = 'UNSAT' if code == cp_model.INFEASIBLE else ('ERROR' if code == cp_model.MODEL_INVALID else 'UNKNOWN')
        if code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            board = [[int(j == solver.value(q[i])) for j in range(n)] for i in range(n)]
            status = 'SAT'
    elif method == 'CPLEX-CP':
        executable = os.environ.get('CPO_EXECUTABLE', 'cpoptimizer.exe')
        if not shutil.which(executable):
            raise FileNotFoundError('CP Optimizer not found; install CPLEX Optimization Studio and set CPO_EXECUTABLE')
        from docplex.cp.model import CpoModel
        model = CpoModel()
        q = model.integer_var_list(n, 0, n-1, name='q')
        model.add(model.all_diff(q))
        model.add(model.all_diff([q[i]+i for i in range(n)]))
        model.add(model.all_diff([q[i]-i for i in range(n)]))
        variables, constraints = n, 3
        built = perf_counter()
        options = dict(TimeLimit=time_limit, Workers=threads, RandomSeed=0, LogVerbosity='Quiet')
        if os.environ.get('CPO_EXECUTABLE'):
            options['execfile'] = os.environ['CPO_EXECUTABLE']
        result = model.solve(**options)
        detail = str(result.get_solve_status())
        status = 'UNSAT' if detail == 'Infeasible' else 'UNKNOWN'
        if result.is_solution():
            board = [[int(j == result.get_value(q[i])) for j in range(n)] for i in range(n)]
            status = 'SAT'
    elif method == 'CPLEX-MIP':
        from docplex.mp.model import Model
        with Model(name='n_queens') as model:
            x = model.binary_var_matrix(n, n, name='x')
            for i in range(n):
                model.add_constraint(model.sum(x[i,j] for j in range(n)) == 1)
            for j in range(n):
                model.add_constraint(model.sum(x[i,j] for i in range(n)) == 1)
            for cells in diagonals(n):
                model.add_constraint(model.sum(x[i,j] for i,j in cells) <= 1)
            model.minimize(0)
            model.parameters.timelimit = time_limit
            model.parameters.threads = threads
            model.parameters.randomseed = 0
            variables, constraints = model.number_of_variables, model.number_of_constraints
            built = perf_counter()
            result = model.solve(log_output=False)
            detail = model.solve_details.status
            status = 'UNSAT' if detail.lower() in ('integer infeasible', 'infeasible') else 'UNKNOWN'
            if result is not None:
                board = [[int(result.get_value(x[i,j]) > .5) for j in range(n)] for i in range(n)]
                status = 'SAT'
    elif method == 'Gurobi-MIP':
        import gurobipy as gp
        from gurobipy import GRB
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.start()
            with gp.Model('n_queens', env=env) as model:
                x = model.addVars(n, n, vtype=GRB.BINARY, name='x')
                model.addConstrs(gp.quicksum(x[i,j] for j in range(n)) == 1 for i in range(n))
                model.addConstrs(gp.quicksum(x[i,j] for i in range(n)) == 1 for j in range(n))
                for cells in diagonals(n):
                    model.addConstr(gp.quicksum(x[i,j] for i,j in cells) <= 1)
                model.setObjective(0)
                model.Params.TimeLimit = time_limit
                model.Params.Threads = threads
                model.Params.Seed = 0
                model.update()
                variables, constraints = model.NumVars, model.NumConstrs
                built = perf_counter()
                model.optimize()
                detail = str(model.Status)
                status = 'UNSAT' if model.Status == GRB.INFEASIBLE else ('TIMEOUT' if model.Status == GRB.TIME_LIMIT else 'UNKNOWN')
                if model.SolCount:
                    board = [[int(x[i,j].X > .5) for j in range(n)] for i in range(n)]
                    status = 'SAT'
    else:
        raise ValueError(f'Unknown method: {method}')
    ended = perf_counter()
    return dict(status=status, solution=board, variables=variables, constraints=constraints, build_time=built-start, solve_time=ended-built, total_time=ended-start, detail=detail)
