import math
from binary import binary_AMO
from binomial import at_most_one as binomial_AMO


def generate_matrix(start, variables_length, n):
    # Chọn lưới gần vuông và đủ ô chứa các biến đầu vào.
    p = math.ceil(math.sqrt(variables_length))
    q = math.ceil(variables_length / p) if p > 0 else 0
    return [[i for i in range(start, start + p)], [j for j in range(start + p, start + p + q)]]


def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    matrix = generate_matrix(n ** 2 + config['new_vars'] + 1, len(variables), n)
    row, col = matrix[0], matrix[1]
    config['new_vars'] += len(row) + len(col)

    # Ngưỡng 10 tính theo số biến đầu vào, không phải số hàng/cột phụ.
    if len(variables) > 10:
        binary_AMO(clauses, row, config, n)
        binary_AMO(clauses, col, config, n)
    else:
        binomial_AMO(clauses, row)
        binomial_AMO(clauses, col)

    # xi đúng thì hàng và cột tương ứng phải đúng. Hai ô khác nhau
    # khác ít nhất một tọa độ nên AMO hàng/cột cấm chọn cả hai.
    # Các ô dư không được gán biến đầu vào.
    x = 0
    for i in range(len(row)):
        for j in range(len(col)):
            if x >= len(variables): break
            clauses.append([-variables[x], row[i]])
            clauses.append([-variables[x], col[j]])
            x += 1

def exactly_one(clauses, variables, config, n):
    # Clause ALO yêu cầu ít nhất một biến đúng; thêm AMO để được đúng một.
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)
