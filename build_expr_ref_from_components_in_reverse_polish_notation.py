"""
Build ExprRef from components in Reverse Polish Notation (akin to Stack Machine Bytecode).

```python
In [1]: from z3 import *

In [2]: x = Int('x')

In [3]: y = Int('y')

In [4]: z = Int('z')

In [5]: e = x + y * z

In [6]: components = list(iterate_components_in_expr_ref_in_reverse_polish_notation(e))

In [7]: components
Out[7]: [x, y, z, (*, 2), (+, 2)]

In [8]: e_ = build_expr_ref_from_components_in_reverse_polish_notation(components)

In [9]: e_
Out[9]: x + y*z

In [10]: e.eq(e_)
Out[10]: True
```
"""

from collections import deque
from sys import stderr

from z3 import *


# Mismatches exist for Z3_OP_AND, Z3_OP_OR, Z3_OP_ADD, Z3_OP_MUL
# Replacement functions are And, Or, Sum, Product
function_kinds_to_mismatching_arity_replacement_functions = {
    Z3_OP_AND: And,
    Z3_OP_OR: Or,
    Z3_OP_ADD: Sum,
    Z3_OP_MUL: Product
}


def build_expr_ref_from_components_in_reverse_polish_notation(
    components_in_reverse_polish_notation,
    function_handler=lambda function, operand_deque: function(*operand_deque)
):
    stack= []

    for component in components_in_reverse_polish_notation:
        if isinstance(component, tuple) and len(component) == 2:
            func, arity = component

            # Handle mismatches between func.arity() and arity
            # Replace func
            if func.arity() != arity:
                # print(f'Mismatch between func.arity()={func.arity()} and {arity} for func={func}', file=stderr)
                # print(f'Replacing func={func} with {function_kinds_to_mismatching_arity_replacement_functions[func.kind()]}', file=stderr)
                func = function_kinds_to_mismatching_arity_replacement_functions[func.kind()]

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
