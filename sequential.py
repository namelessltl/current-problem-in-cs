def generate_new_variables(new_variables_count, length, n):
    # Auxiliary IDs start after the board variables and earlier counters.
    start = n ** 2 + new_variables_count
    return [i for i in range(start + 1, start + length)]

def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    new_variables = generate_new_variables(config['new_vars'], len(variables), n)
    config['new_vars'] += (len(variables) - 1)
    clauses.append([-variables[0], new_variables[0]])
    # Carry the previous selection forward and prevent a second true input.
    for i in range(1, len(variables) - 1):
        clauses.append([-variables[i], new_variables[i]])
        clauses.append([-new_variables[i - 1], new_variables[i]])
        clauses.append([-new_variables[i - 1], -variables[i]])
    clauses.append([-new_variables[len(variables) - 2], -variables[len(variables) - 1]])

def exactly_one(clauses, variables, config, n):
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)
