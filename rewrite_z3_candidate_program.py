"""
```python
In [1]: from z3 import *

In [2]: x = Int('x')

In [3]: y = Int('y')

In [4]: z = Int('z')

In [5]: z3_candidate_program = x * If(x < y, x + 1, 2 * y)

In [6]: z3_candidate_program
Out[6]: x*If(x < y, x + 1, 2*y)

In [7]: z3_input_variables_to_operands = {x: x - 2 * y, y: x * y}

In [8]: rewrite_z3_candidate_program(z3_candidate_program, z3_input_variables_to_operands)
Out[8]: (x - 2*y)*If(x - 2*y < x*y, x - 2*y + 1, 2*x*y)
```
"""

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation


def rewrite_z3_candidate_program(z3_candidate_program, z3_input_variables_to_operands):
    z3_candidate_program_components = iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(
        z3_candidate_program
    )

    rewritten_z3_candidate_program_components = (
        z3_input_variables_to_operands[component] if component in z3_input_variables_to_operands else component
        for component in z3_candidate_program_components
    )

    rewritten_z3_candidate_program = build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
        rewritten_z3_candidate_program_components
    )

    return rewritten_z3_candidate_program
