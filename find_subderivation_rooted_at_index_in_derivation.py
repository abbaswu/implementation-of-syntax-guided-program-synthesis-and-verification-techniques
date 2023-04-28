"""
In [1]: from z3 import *

In [2]: from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import *

In [3]: z3_x = Int('x')

In [4]: z3_y = Int('y')

In [5]: expression = If(z3_x >= z3_y, z3_x + z3_y, z3_y - z3_x)

In [6]: derivation = tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(expression))

In [7]: derivation
Out[7]: (x, y, (>=, 2), x, y, (+, 2), y, x, (-, 2), (If, 3))

In [10]: find_subderivation_rooted_at_index_in_derivation(derivation, 0)
Out[10]: (x,)

In [11]: find_subderivation_rooted_at_index_in_derivation(derivation, 1)
Out[11]: (y,)

In [12]: find_subderivation_rooted_at_index_in_derivation(derivation, 2)
Out[12]: (x, y, (>=, 2))

In [13]: find_subderivation_rooted_at_index_in_derivation(derivation, 3)
Out[13]: (x,)

In [14]: find_subderivation_rooted_at_index_in_derivation(derivation, 4)
Out[14]: (y,)

In [15]: find_subderivation_rooted_at_index_in_derivation(derivation, 5)
Out[15]: (x, y, (+, 2))

In [16]: find_subderivation_rooted_at_index_in_derivation(derivation, 6)
Out[16]: (y,)

In [17]: find_subderivation_rooted_at_index_in_derivation(derivation, 7)
Out[17]: (x,)

In [18]: find_subderivation_rooted_at_index_in_derivation(derivation, 8)
Out[18]: (y, x, (-, 2))

In [19]: find_subderivation_rooted_at_index_in_derivation(derivation, 9)
Out[19]: (x, y, (>=, 2), x, y, (+, 2), y, x, (-, 2), (If, 3))
"""

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
