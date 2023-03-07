"""
Iterates components in ExprRef in Reverse Polish Notation (akin to Stack Machine Bytecode).

```python
In [1]: from z3 import *

In [2]: x = Int('x')

In [3]: y = Int('y')

In [4]: z = Int('z')

In [5]: e = x + y * z

In [6]: components = list(iterate_components_in_expr_ref_in_reverse_polish_notation(e))

In [7]: components
Out[7]: [x, y, z, (*, 2), (+, 2)]
```
"""


def iterate_components_in_expr_ref_in_reverse_polish_notation(expr_ref):
    num_args = expr_ref.num_args()
    # Expression with multiple variables
    if num_args:
        for i in range(num_args):
            yield from iterate_components_in_expr_ref_in_reverse_polish_notation(expr_ref.arg(i))
        yield (expr_ref.decl(), num_args)
    # Expression with one variable
    else:
        yield expr_ref
