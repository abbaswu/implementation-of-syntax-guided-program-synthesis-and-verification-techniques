"""
```python
In [1]: from z3 import *

In [2]: x = Int('x')

In [3]: y = Int('y')

In [4]: z3_input_variable_list = [x, y]

In [5]: z3_function_declaration = max2 = Function('max2', IntSort(), IntSort(), IntSort())

In [6]: z3_constraint = And(max2(x, y) >= x, max2(x, y) >= y, Or(max2(y, x) == x, max2(y, x) == y))

In [8]: v = z3_verification_oracle(z3_input_variable_list, z3_function_declaration, z3_constraint)

In [9]: next(v)

In [10]: v.send(x)
Out[10]: ({x: -1, y: 0}, -1)

In [11]: v.send(y)
Out[11]: ({x: 0, y: -1}, -1)

In [12]: v.send(If(x >= y, x, y))
```
"""

from frozendict import frozendict
import z3

from evaluate_z3_expr_ref import evaluate_z3_expr_ref
from replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program import replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program


def z3_verification_oracle(z3_input_variable_list, z3_function_declaration, z3_constraint):
    assert len(z3_input_variable_list) == z3_function_declaration.arity()

    # Get first candidate program
    z3_candidate_program = yield
    while True:
        solver = z3.Solver()
        solver.add(
            z3.Not(
                replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program(
                    z3_input_variable_list,
                    z3_function_declaration,
                    z3_constraint,
                    z3_candidate_program
                )
            )
        )
        check_sat_result = solver.check()
        if check_sat_result == z3.sat:
            model_ref = solver.model()
            # Get next candidate program and yield counterexample
            z3_input_variables_to_values = frozendict((
                (z3_input_variable, model_ref[z3_input_variable])
                for z3_input_variable in z3_input_variable_list
            ))
            z3_candidate_program = yield z3_input_variables_to_values
        elif check_sat_result == z3.unsat:
            # Get next candidate program and yield None
            z3_candidate_program = yield None
        else:
            assert False
