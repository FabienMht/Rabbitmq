import sys, ast
from itertools import permutations

def is_safe(permutation):
    size = len(permutation)
    for i in range(size):
        for j in range(i + 1, size):
            if abs(permutation[i] - permutation[j]) == abs(i - j):
                return False
    return True

def solve(input_list_base):
    input_list_permut = []
    solutions = []

    for pos in list(range(len(input_list_base))):
        if pos not in input_list_base:
            input_list_permut.append(pos)

    input_list_base=list(filter((-1).__ne__, input_list_base))

    for permutation in permutations(input_list_permut):
        permutation=list(permutation)
        permutation=input_list_base+permutation
        if is_safe(permutation):
            solutions.append(permutation)
    return len(solutions)

inputList = ast.literal_eval(sys.argv[1])
print(solve(inputList))
