import math


def binary_encoding(clauses, target, new_variables):
    for i in range(len(new_variables)):
        clauses.append([-target, new_variables[i]])

def generate_binary_combinations(n):
    return [format(i, '0' + str(n) + 'b') for i in range(1 << n)]

def generate_new_variables(end, length):
    return [i for i in range(end + 1, end + math.ceil(math.log(length, 2)) + 1)]

def at_most_one(clauses, new_variables, variables, n):
    if len(variables) < 2: return
    # Each input gets a different bit pattern, so two cannot be true together.
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
    # At least one, combined with at most one, gives exactly one.
    clauses.append(variables)
    at_most_one(clauses, new_variables, variables, n)
