import math


def binary_encoding(clauses, target, new_variables):
    for i in range(len(new_variables)):
        clauses.append([-target, new_variables[i]])

def generate_binary_combinations(n):
    return [format(i, '0' + str(n) + 'b') for i in range(1 << n)]

def generate_new_variables(end, length):
    return [i for i in range(end + 1, end + math.ceil(math.log(length, 2)) + 1)]

def encode_amo(clauses, variables, end):
    if len(variables) < 2:
        return []
    temp_new_variables = generate_new_variables(end, len(variables))
    binary_combinations = generate_binary_combinations(len(temp_new_variables))

    for i in range(len(variables)):
        combination = binary_combinations[i]
        temp_clause = []
        for j in range(len(combination) - 1, -1, -1):
            index = len(combination) - j - 1
            temp_clause.append(temp_new_variables[index] if int(combination[j]) == 1 else -temp_new_variables[index])
        binary_encoding(clauses, variables[i], temp_clause)
    return temp_new_variables


def at_most_one(clauses, new_variables, variables, n):
    # Binary dùng riêng thì lưu các biến phụ vào danh sách.
    allocated = encode_amo(clauses, variables, n ** 2 + len(new_variables))
    new_variables.extend(allocated)


def binary_AMO(clauses, variables, config, n):
    # Commander/Product dùng bộ đếm; vẫn gọi cùng một phần mã hóa ở trên.
    allocated = encode_amo(clauses, variables, n ** 2 + config['new_vars'])
    config['new_vars'] += len(allocated)

def exactly_one(clauses, new_variables, variables, n):
    # Clause ALO yêu cầu ít nhất một biến đúng; thêm AMO để được đúng một.
    clauses.append(variables)
    at_most_one(clauses, new_variables, variables, n)
