import math
from pysat.solvers import Glucose3

def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def binomial_AMO(clauses, variables):
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])
    return clauses

def generate_matrix(start, variables_length, n):
    p = math.ceil(math.sqrt(variables_length))
    q = math.ceil(n / p) if p > 0 else 0
    return [[i for i in range(start, start + p)], [j for j in range(start + p, start + p + q)]]

def generate_binary_combinations(length):
    return [format(i, '0' + str(length) + 'b') for i in range(1 << length)]

def binary_encoding(clauses, target, new_variables):
    for i in range(len(new_variables)):
        clauses.append([-target, new_variables[i]])

def generate_new_variables(end, length):
    return [i for i in range(end + 1, end + math.ceil(math.log(length, 2)) + 1)]

def binary_AMO(clauses, variables, config, n):
    if len(variables) < 2: return
    temp_new_variables = generate_new_variables(n ** 2 + config['new_vars'], len(variables))
    config['new_vars'] += len(temp_new_variables)
    binary_combinations = generate_binary_combinations(len(temp_new_variables))

    for i in range(len(variables)):
        combination = binary_combinations[i]
        temp_clause = []
        for j in range(len(combination) - 1, -1, -1):
            index = len(combination) - j - 1
            temp_clause.append(temp_new_variables[index] if int(combination[j]) == 1 else -temp_new_variables[index])
        binary_encoding(clauses, variables[i], temp_clause)

def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    matrix = generate_matrix(n ** 2 + config['new_vars'] + 1, len(variables), n)
    row, col = matrix[0], matrix[1]
    config['new_vars'] += len(row) + len(col)

    if len(variables) > 10:
        binary_AMO(clauses, row, config, n)
        binary_AMO(clauses, col, config, n)
    else:
        binomial_AMO(clauses, row)
        binomial_AMO(clauses, col)

    x = 0
    for i in range(len(row)):
        for j in range(len(col)):
            if x >= len(variables): break
            clauses.append([-variables[x], row[i]])
            clauses.append([-variables[x], col[j]])
            x += 1

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
    variables = generate_variables(n)
    clauses, new_vars_count = generate_clauses(n, variables)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)
    if solver.solve():
        model = solver.get_model()
        return [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)], n**2 + new_vars_count, len(clauses)
    return None, 0, 0