# https://docs.sympy.org/latest/tutorials/intro-tutorial/manipulation.html#tutorial-manipulation

"""
Iterates components in Expr in Reverse Polish Notation (akin to Stack Machine Bytecode).
`func`'s represented as 2-tuple's containing the `func` and the number of `args`.

```python
In [1]: from sympy import *

In [2]: x = symbols('x')

In [3]: y = symbols('y')

In [4]: z = symbols('z')

In [5]: e = x + y * z

In [6]: components = list(iterate_components_in_expr_in_reverse_polish_notation(e))

In [7]: components
Out[7]: [x, y, z, (sympy.core.mul.Mul, 2), (sympy.core.add.Add, 2)]
```
"""


def iterate_components_in_expr_in_reverse_polish_notation(expr):
    args = expr.args
    # Expression with multiple variables
    if args:
        for arg in args:
            yield from iterate_components_in_expr_in_reverse_polish_notation(arg)
        yield (expr.func, len(args))
    # Expression with one variable
    else:
        yield expr
