def at_most_one(clauses, variables):
    # Mỗi cặp xi, xj nhận clause (-xi OR -xj).
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])
    return clauses

def exactly_one(clauses, variables):
    # Clause ALO yêu cầu ít nhất một biến đúng; thêm AMO để được đúng một.
    clauses.append(variables)
    at_most_one(clauses, variables)
