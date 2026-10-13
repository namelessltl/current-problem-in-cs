from pysat.solvers import Glucose3

def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def generate_new_variables(new_variables_count, length, n):
    start = n ** 2 + new_variables_count
    return [i for i in range(start + 1, start + length)]

def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    new_variables = generate_new_variables(config['new_vars'], len(variables), n)
    config['new_vars'] += (len(variables) - 1)
    clauses.append([-variables[0], new_variables[0]])
    for i in range(1, len(variables) - 1):
        clauses.append([-variables[i], new_variables[i]])
        clauses.append([-new_variables[i - 1], new_variables[i]])
        clauses.append([-new_variables[i - 1], -variables[i]])
    clauses.append([-new_variables[len(variables) - 2], -variables[len(variables) - 1]])

def exactly_one(clauses, variables, config, n):
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)

def generate_clauses(n, variables):
    clauses = []
    config = {'new_vars': 0}
    for row in range(n):
        exactly_one(clauses, variables[row], config, n)
    for col in range(n):
        exactly_one(clauses, [variables[row][col] for row in range(n)], config, n)
    
    for i in range(1, n):
        diagonal = [variables[i-k][k] for k in range(n) if 0 <= i-k < n and 0 <= k < n]
        at_most_one(clauses, diagonal, config, n)
    for j in range(1, n - 1):
        diagonal = [variables[n-1-k][j+k] for k in range(n) if 0 <= n-1-k < n and 0 <= j+k < n]
        at_most_one(clauses, diagonal, config, n)
    for i in range(n - 1):
        diagonal = [variables[i+k][k] for k in range(n) if 0 <= i+k < n and 0 <= k < n]
        at_most_one(clauses, diagonal, config, n)
    for j in range(1, n - 1):
        diagonal = [variables[k][j+k] for k in range(n) if 0 <= k < n and 0 <= j+k < n]
        at_most_one(clauses, diagonal, config, n)
    return clauses, config['new_vars']

def solve_n_queens(n):
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    variables = generate_variables(n)
    clauses, new_vars_count = generate_clauses(n, variables)
    vars_count = n * n + new_vars_count
    with Glucose3(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None, vars_count, len(clauses)
        positive = {literal for literal in solver.get_model() if literal > 0}
        solution = [[int(variables[i][j] in positive) for j in range(n)]
                    for i in range(n)]
        return solution, vars_count, len(clauses)

if __name__ == "__main__":
    import argparse
    from time import perf_counter

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    args = parser.parse_args()
    start = perf_counter()
    solution, variables_count, clauses_count = solve_n_queens(args.n)
    elapsed = perf_counter() - start
    print("SAT" if solution is not None else "UNSAT")
    print(f"Variables: {variables_count}, Clauses: {clauses_count}")
    print(f"Time: {elapsed:.6f} s")
    if solution is not None and args.n <= 20:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))
