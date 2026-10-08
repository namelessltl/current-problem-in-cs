import math
from pysat.solvers import Glucose3

def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def binary_encoding(clauses, target, new_variables):
    for i in range(len(new_variables)):
        clauses.append([-target, new_variables[i]])

def generate_binary_combinations(n):
    return [format(i, '0' + str(n) + 'b') for i in range(1 << n)]

def generate_new_variables(end, length):
    return [i for i in range(end + 1, end + math.ceil(math.log(length, 2)) + 1)]

def at_most_one(clauses, new_variables, variables, n):
    if len(variables) < 2: return
    temp_new_variables = generate_new_variables(n ** 2 + len(new_variables), len(variables))
    new_variables.extend(temp_new_variables)
    binary_combinations = generate_binary_combinations(len(temp_new_variables))

    for i in range(len(variables)):
        combination = binary_combinations[i]
        temp_clause = []
        for j in range(len(combination) - 1, -1, -1):
            index = len(combination) - j - 1
            temp_clause.append(temp_new_variables[index] if int(combination[j]) == 1 else -temp_new_variables[index])
        binary_encoding(clauses, variables[i], temp_clause)

def exactly_one(clauses, new_variables, variables, n):
    clauses.append(variables)
    at_most_one(clauses, new_variables, variables, n)

def generate_clauses(n, variables):
    clauses, new_variables = [], []
    for i in range(n):
        exactly_one(clauses, new_variables, variables[i], n)
    for j in range(n):
        exactly_one(clauses, new_variables, [variables[i][j] for i in range(n)], n)

    for i in range(1, n):
        diagonal = [variables[i-k][k] for k in range(n) if 0 <= i-k < n and 0 <= k < n]
        at_most_one(clauses, new_variables, diagonal, n)
    for j in range(1, n - 1):
        diagonal = [variables[n-1-k][j+k] for k in range(n) if 0 <= n-1-k < n and 0 <= j+k < n]
        at_most_one(clauses, new_variables, diagonal, n)
    for i in range(n - 1):
        diagonal = [variables[i+k][k] for k in range(n) if 0 <= i+k < n and 0 <= k < n]
        at_most_one(clauses, new_variables, diagonal, n)
    for j in range(1, n - 1):
        diagonal = [variables[k][j+k] for k in range(n) if 0 <= k < n and 0 <= j+k < n]
        at_most_one(clauses, new_variables, diagonal, n)
    return clauses, new_variables

def solve_n_queens(n):
    variables = generate_variables(n)
    clauses, new_vars = generate_clauses(n, variables)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)
    if solver.solve():
        model = solver.get_model()
        return [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)], n**2 + len(new_vars), len(clauses)
    return None, 0, 0