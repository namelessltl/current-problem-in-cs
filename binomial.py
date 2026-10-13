from pysat.solvers import Glucose3

def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def at_most_one(clauses, variables):
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])
    return clauses

def exactly_one(clauses, variables):
    clauses.append(variables)
    at_most_one(clauses, variables)

def generate_clauses(n, variables):
    clauses = []
    for i in range(n):
        exactly_one(clauses, variables[i])
    for j in range(n):
        exactly_one(clauses, [variables[i][j] for i in range(n)])
    for i in range(n):
        for j in range(n):
            for k in range(1, n):
                if i + k < n and j + k < n:
                    at_most_one(clauses, [variables[i][j], variables[i + k][j + k]])
                if i + k < n and j - k >= 0:
                    at_most_one(clauses, [variables[i][j], variables[i + k][j - k]])
    return clauses

def solve_n_queens(n):
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    variables = generate_variables(n)
    clauses = generate_clauses(n, variables)
    vars_count = n * n
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
