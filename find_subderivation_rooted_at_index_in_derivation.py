from collections import deque


def find_subderivation_rooted_at_index_in_derivation(derivation, index):
    symbol_at_index = derivation[index]
    if isinstance(symbol_at_index, tuple) and len(symbol_at_index) == 2:
        func, arity = symbol_at_index

        subderivations_of_operands_deque = deque()
        index_of_operand = index - 1
        for _ in range(arity):
            subderivation_of_operand = find_subderivation_rooted_at_index_in_derivation(
                derivation[:(index_of_operand + 1)],
                index_of_operand
            )
            subderivations_of_operands_deque.extendleft(subderivation_of_operand[::-1])
            index_of_operand -= len(subderivation_of_operand)

        subderivations_of_operands_deque.append(symbol_at_index)

        return tuple(subderivations_of_operands_deque)
    else:
        return (symbol_at_index,)


if __name__ == '__main__':
    from z3 import *
    from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import *

    z3_x = Int('x')
    z3_y = Int('y')
    expression = If(z3_x >= z3_y, z3_x + z3_y, z3_y - z3_x)
    derivation = tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(expression))

    while True:
        i = int(input())
        print(find_subderivation_rooted_at_index_in_derivation(derivation, i))
