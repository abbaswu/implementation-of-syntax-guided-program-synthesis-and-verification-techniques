"""
``python
In [1]: from sympy import *

In [2]: x = Symbol('x')

In [3]: y = Symbol('y')

In [4]: input_variable_list = [x, y]

In [5]: function_declaration = max2 = Function('max2')

In [6]: constraint = And(GreaterThan(max2(x, y), x), GreaterThan(max2(x, y), y), Or(Equality(max2(y, x), x), Equality(max2(y, x), y)))

In [7]: candidate_program = Piecewise((x, x >= y), (y, True))

In [8]: replace_function_declaration_in_constraint_with_candidate_program(input_variable_list, function_declaration, constraint, candidate_program)
Out[8]: (Piecewise((x, x >= y), (y, True)) >= x) & (Piecewise((x, x >= y), (y, True)) >= y) & (Eq(Piecewise((y, x <= y), (x, True)), x) | Eq(Piecewise((y, x <= y), (x, True)), y))
```
"""

from sympy import FunctionClass

from build_expr_from_components_in_reverse_polish_notation import build_expr_from_components_in_reverse_polish_notation
from iterate_components_in_expr_in_reverse_polish_notation import iterate_components_in_expr_in_reverse_polish_notation
from rewrite_candidate_program import rewrite_candidate_program


def replace_function_declaration_in_constraint_with_candidate_program(
        input_variable_list,
        function_declaration,
        constraint,
        candidate_program
):
    def handle_function_declaration(function, operand_deque):
        nonlocal input_variable_list, function_declaration, candidate_program

        input_variables_to_operands = {
            input_variable: operand
            for input_variable, operand in zip(input_variable_list, operand_deque)
        }

        if isinstance(function, FunctionClass) and function == function_declaration:
            return rewrite_candidate_program(candidate_program, input_variables_to_operands)
        else:
            return function(*operand_deque)

    return build_expr_from_components_in_reverse_polish_notation(
        iterate_components_in_expr_in_reverse_polish_notation(constraint),
        handle_function_declaration
    )
