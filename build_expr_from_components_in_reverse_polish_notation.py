# https://docs.sympy.org/latest/tutorials/intro-tutorial/manipulation.html#tutorial-manipulation

"""
Build Expr from components in Reverse Polish Notation (akin to Stack Machine Bytecode).
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

In [8]: e_ = build_expr_from_components_in_reverse_polish_notation(components)

In [9]: e_
Out[9]: x + y*z

In [10]: e == e_
Out[10]: True

In [11]: components_ = [components[1], components[2], components[3], components[0], components[4]]

In [12]: components_
Out[12]: [y, z, (sympy.core.mul.Mul, 2), x, (sympy.core.add.Add, 2)]

In [13]: e__ = build_expr_from_components_in_reverse_polish_notation(components_)

In [14]: e__
Out[14]: x + y*z

In [15]: e == e__
Out[15]: True
```
"""

from collections import deque

import sympy


def build_expr_from_components_in_reverse_polish_notation(
    components_in_reverse_polish_notation,
    function_handler=lambda function, operand_deque: function(*operand_deque)
):
    stack= []

    for component in components_in_reverse_polish_notation:
        if isinstance(component, tuple) and len(component) == 2:

            func, arity = component

            assert len(stack) >= arity

            operand_deque = deque()
            for _ in range(arity):
                operand_deque.appendleft(stack.pop())

            return_value = function_handler(func, operand_deque)

            stack.append(return_value)
        else:
            stack.append(component)
    
    assert len(stack) == 1
    return stack.pop()
