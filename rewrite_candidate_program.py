"""
```python
In [1]: from sympy import *

In [2]: x = Symbol('x')

In [3]: y = Symbol('y')

In [4]: z = Symbol('z')

In [5]: candidate_program = x * Piecewise((x + 1, x < y), (2 * y, True))

In [6]: candidate_program
Out[6]: x*Piecewise((x + 1, x < y), (2*y, True))

In [7]: input_variables_to_operands = {x: x - 2 * y, y: x * y}

In [8]: rewrite_candidate_program(candidate_program, input_variables_to_operands)
Out[8]: (x - 2*y)*Piecewise((x - 2*y + 1, x*y > x - 2*y), (2*x*y, True))
```
"""

from build_expr_from_components_in_reverse_polish_notation import build_expr_from_components_in_reverse_polish_notation
from iterate_components_in_expr_in_reverse_polish_notation import iterate_components_in_expr_in_reverse_polish_notation


def rewrite_candidate_program(candidate_program, input_variables_to_operands):
    candidate_program_components = iterate_components_in_expr_in_reverse_polish_notation(
        candidate_program
    )

    rewritten_candidate_program_components = (
        input_variables_to_operands[component] if component in input_variables_to_operands else component
        for component in candidate_program_components
    )

    rewritten_candidate_program = build_expr_from_components_in_reverse_polish_notation(
        rewritten_candidate_program_components
    )

    return rewritten_candidate_program
