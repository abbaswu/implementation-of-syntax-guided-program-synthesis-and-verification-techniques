"""
``python
In [1]: from z3 import *

In [2]: x = Int('x')

In [3]: y = Int('y')

In [4]: z3_input_variable_list = [x, y]

In [5]: z3_function_declaration = max2 = Function('max2', IntSort(), IntSort(), IntSort())

In [6]: z3_constraint = And(max2(x, y) >= x, max2(x, y) >= y, Or(max2(y, x) == x, max2(y, x) == y))

In [7]: z3_candidate_program = If(x >= y, x, y)

In [8]: replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program(z3_input_variable_list, z3_function_declaration, z3_constraint, z3_candidate_program)
Out[8]: 
And(If(x >= y, x, y) >= x,
    If(x >= y, x, y) >= y,
    Or(If(y >= x, y, x) == x, If(y >= x, y, x) == y))
```
"""

from z3 import AstRef

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import \
    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation
from rewrite_z3_candidate_program import rewrite_z3_candidate_program


def replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program(
        z3_input_variable_list,
        z3_function_declaration,
        z3_constraint,
        z3_candidate_program
):
    def handle_z3_function_declaration(function, operand_deque):
        nonlocal z3_input_variable_list, z3_function_declaration, z3_candidate_program

        z3_input_variables_to_operands = {
            z3_input_variable: operand
            for z3_input_variable, operand in zip(z3_input_variable_list, operand_deque)
        }

        if isinstance(function, AstRef) and function == z3_function_declaration:
            return rewrite_z3_candidate_program(z3_candidate_program, z3_input_variables_to_operands)
        else:
            return function(*operand_deque)

    return build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
        iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_constraint),
        handle_z3_function_declaration
    )
