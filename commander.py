# Commander: chia nhóm, dùng một biến đại diện cho mỗi nhóm.
# AMO giữa các commander dùng Pairwise; trong nhóm dùng Binary hoặc Pairwise.
# CNF: mỗi list trong clauses là một phép OR; số âm biểu diễn phủ định.
import math
from binary import binary_AMO
from binomial import at_most_one as binomial_AMO


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


def at_most_one(clauses, variables, config, n):
    if len(variables) < 2: return
    # Kích thước nhóm tính theo cạnh bàn cờ n, không theo độ dài AMO.
    per_group = max(1, int(n / math.floor(math.sqrt(n))))
    groups = grouping_variables(variables, per_group)
    commanders = generate_commanders(n ** 2 + config['new_vars'] + 1, len(groups))
    config['new_vars'] += len(groups)
    # Tối đa một commander đúng, tức tối đa một nhóm được chọn.
    binomial_AMO(clauses, commanders)

    for i in range(len(commanders)):
        # Nhóm hơn 4 biến dùng Binary, nhóm nhỏ dùng Pairwise.
        if len(groups[i]) > 4:
            binary_AMO(clauses, groups[i], config, n)
        else:
            binomial_AMO(clauses, groups[i])
        # commander -> OR(nhóm); từng biến trong nhóm -> commander.
        clauses.append(groups[i] + [-commanders[i]])
        for j in range(len(groups[i])):
            clauses.append([commanders[i], -groups[i][j]])

def exactly_one(clauses, variables, config, n):
    # Clause ALO yêu cầu ít nhất một biến đúng; thêm AMO để được đúng một.
    clauses.append(variables)
    at_most_one(clauses, variables, config, n)
