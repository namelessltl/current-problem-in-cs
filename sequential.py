def generate_new_variables(new_variables_count, length, n):
    # Cấp k - 1 biến phụ, tránh trùng ID với bàn cờ và các bộ đếm trước.
    start = n ** 2 + new_variables_count
    return [i for i in range(start + 1, start + length)]

def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    new_variables = generate_new_variables(config['new_vars'], len(variables), n)
    config['new_vars'] += (len(variables) - 1)
    clauses.append([-variables[0], new_variables[0]])
    # xi bật thì si bật; si-1 truyền sang si và cấm xi bật thêm.
    for i in range(1, len(variables) - 1):
        clauses.append([-variables[i], new_variables[i]])
        clauses.append([-new_variables[i - 1], new_variables[i]])
        clauses.append([-new_variables[i - 1], -variables[i]])
    # Đã có biến đúng phía trước thì biến cuối phải sai.
    clauses.append([-new_variables[len(variables) - 2], -variables[len(variables) - 1]])

def exactly_one(clauses, variables, config, n):
    # Clause ALO yêu cầu ít nhất một biến đúng; thêm AMO để được đúng một.
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)
