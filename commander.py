import math


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

def grouping_variables(variables, per_group):
    groups, temp_groups = [], []
    for i in range(len(variables)):
        temp_groups.append(variables[i])
        if (i + 1) % per_group == 0 or i == len(variables) - 1:
            groups.append(temp_groups)
            temp_groups = []
    return groups

def generate_commanders(start, length):
    return [i for i in range(start, start + length)]

def binomial_AMO(clauses, variables):
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])
    return clauses

def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    # Use one commander per group, then restrict the commanders themselves.
    per_group = max(1, int(n / math.floor(math.sqrt(n))))
    groups = grouping_variables(variables, per_group)
    commanders = generate_commanders(n ** 2 + config['new_vars'] + 1, len(groups))
    config['new_vars'] += len(groups)
    binomial_AMO(clauses, commanders)

    for i in range(len(commanders)):
        if len(groups[i]) > 4:
            binary_AMO(clauses, groups[i], config, n)
        else:
            binomial_AMO(clauses, groups[i])
        # The commander is true exactly when its group contains a true input.
        clauses.append(groups[i] + [-commanders[i]])
        for j in range(len(groups[i])):
            clauses.append([commanders[i], -groups[i][j]])

def exactly_one(clauses, variables, config, n):
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)
