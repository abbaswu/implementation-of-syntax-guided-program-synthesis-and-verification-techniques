"""
```python
In [1]: from sympy import *

In [2]: x = Symbol('x')

In [3]: y = Symbol('y')

In [4]: input_variables_to_value_iterables = {x: range(10), y: range(10)}

In [5]: function_declaration = max2 = Function('max2')

In [6]: constraint = And(GreaterThan(max2(x, y), x), GreaterThan(max2(x, y), y), Or(Equality(max2(y, x), x), Equality(max2(y, x), y)))

In [8]: v = enumerative_verification_oracle(input_variables_to_value_iterables, function_declaration, constraint)

In [9]: next(v)

In [10]: v.send(x)
Out[10]: (frozendict.frozendict({x: 0, y: 1}), 0)

In [11]: v.send(y)
Out[11]: (frozendict.frozendict({x: 1, y: 0}), 0)

In [12]: v.send(x + y)
Out[12]: (frozendict.frozendict({x: 1, y: 1}), 2)

In [13]: v.send(Piecewise((y, x >= y), (x, True)))
Out[13]: (frozendict.frozendict({x: 0, y: 1}), 0)

In [14]: v.send(Piecewise((x, x >= y), (y, True)))
```
"""

import itertools

import sympy
from frozendict import frozendict

from replace_function_declaration_in_constraint_with_candidate_program import \
    replace_function_declaration_in_constraint_with_candidate_program


def enumerative_verification_oracle(input_variables_to_value_iterables, function_declaration, constraint):
    # Get first candidate program
    candidate_program = yield
    while True:
        # Replace function_declaration in constraint with candidate_program
        modified_constraint = replace_function_declaration_in_constraint_with_candidate_program(
            input_variables_to_value_iterables.keys(),
            function_declaration,
            constraint,
            candidate_program
        )

        # Convert a SymPy expression into a function that allows for fast numeric evaluation.
        lambdified_modified_constraint = sympy.lambdify(input_variables_to_value_iterables.keys(), modified_constraint)

        # Iterate over all input variable values
        for input_variable_value_tuple in itertools.product(*input_variables_to_value_iterables.values()):
            # Found a input_variable_value_tuple that does not satisfy lambdified_modified_constraint
            # This is a counterexample
            if not lambdified_modified_constraint(*input_variable_value_tuple):
                # Get next candidate program and yield counterexample
                input_variables_to_values_frozendict = frozendict(
                    zip(input_variables_to_value_iterables.keys(), input_variable_value_tuple))
                candidate_program = yield input_variables_to_values_frozendict
                # Stop iterating over all input variable values
                break
        # Failed to find a input_variable_value_tuple that does not satisfy lambdified_modified_constraint
        else:
            # Get next candidate program and yield None
            candidate_program = yield None
