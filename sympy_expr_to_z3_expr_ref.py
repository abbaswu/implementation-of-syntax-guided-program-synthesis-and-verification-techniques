"""
Transform a sympy Expr to a z3 ExprRef.

```python
In [1]: import sympy

In [2]: import z3

In [3]: from sympy_expr_to_z3_expr_ref import sympy_expr_to_z3_expr_ref

In [4]: sympy_x, sympy_y, sympy_z = sympy.symbols('x y z')

In [5]: z3_x, z3_y, z3_z = z3.Ints('x y z')

In [6]: sympy_symbols_to_z3_expr_ref = {sympy_x: z3_x, sympy_y: z3_y, sympy_z: z3_z}

In [7]: sympy_expr = sympy_x * sympy.Piecewise((sympy_x + 1, sympy_x < sympy_y), (2 * sympy_y, True))

In [8]: sympy_expr
Out[8]: x*Piecewise((x + 1, x < y), (2*y, True))

In [9]: sympy_expr_to_z3_expr_ref(sympy_symbols_to_z3_expr_ref, sympy_expr)
Out[9]: x*If(x < y, 1 + x, 2*y)
```
"""

from functools import reduce

import sympy
import z3


# https://docs.sympy.org/latest/modules/core.html#module-sympy.core.numbers
# https://docs.sympy.org/latest/modules/logic.html
# https://z3prover.github.io/api/html/z3py_8py_source.html#l03188

def sympy_expr_to_z3_expr_ref(sympy_symbols_to_z3_expr_ref, expr):
    args = expr.args
    # Non atoms
    if args:
        # Special handling for sympy.Piecewise
        if isinstance(expr, sympy.Piecewise):
            z3_expressions = [sympy_expr_to_z3_expr_ref(sympy_symbols_to_z3_expr_ref, arg.expr) for arg in expr.args]
            z3_conditions = [sympy_expr_to_z3_expr_ref(sympy_symbols_to_z3_expr_ref, arg.cond) for arg in expr.args]

            last_z3_expression = z3_expressions[-1]
            last_z3_condition = z3_conditions[-1]

            assert last_z3_condition.eq(z3.BoolVal(True))

            return reduce(
                lambda last_returned_expression, new_expression_condition_pair: z3.If(new_expression_condition_pair[1],
                                                                                      new_expression_condition_pair[0],
                                                                                      last_returned_expression),
                zip(z3_expressions[-2::-1], z3_conditions[-2::-1]),
                last_z3_expression
            )
        else:
            z3_args = [sympy_expr_to_z3_expr_ref(sympy_symbols_to_z3_expr_ref, arg) for arg in expr.args]

            if isinstance(expr, sympy.Add):
                return z3.Sum(*z3_args)
            elif isinstance(expr, sympy.Mul):
                return z3.Product(*z3_args)
            elif isinstance(expr, sympy.Mod):
                p, q = z3_args
                return p % q
            elif isinstance(expr, sympy.Pow):
                b, e = z3_args
                return b ** e
            elif isinstance(expr, sympy.Equality):
                lhs, rhs = z3_args
                return lhs == rhs
            elif isinstance(expr, sympy.Unequality):
                lhs, rhs = z3_args
                return lhs != rhs
            elif isinstance(expr, sympy.StrictLessThan):
                lhs, rhs = z3_args
                return lhs < rhs
            elif isinstance(expr, sympy.LessThan):
                lhs, rhs = z3_args
                return lhs <= rhs
            elif isinstance(expr, sympy.StrictGreaterThan):
                lhs, rhs = z3_args
                return lhs > rhs
            elif isinstance(expr, sympy.GreaterThan):
                lhs, rhs = z3_args
                return lhs >= rhs
            elif isinstance(expr, sympy.And):
                return z3.And(*z3_args)
            elif isinstance(expr, sympy.Or):
                return z3.Or(*z3_args)
            elif isinstance(expr, sympy.Not):
                p, *_ = z3_args
                return z3.Not(p)
            # sympy.Xor, sympy.Nand, sympy.Nor, sympy.Xnor, sympy.Implies, sympy.Equivalent, sympy.ITE, sympy.Exclusive skipped
            else:
                assert False, type(expr)
    # Atoms
    else:
        if isinstance(expr, sympy.Symbol):
            return sympy_symbols_to_z3_expr_ref[expr]
        elif isinstance(expr, sympy.Integer):
            return z3.IntVal(str(expr))
        elif isinstance(expr, sympy.Rational):
            return z3.RealVal(str(expr))
        elif isinstance(expr, sympy.logic.boolalg.BooleanTrue):
            return z3.BoolVal(True)
        elif isinstance(expr, sympy.logic.boolalg.BooleanFalse):
            return z3.BoolVal(False)
        else:
            assert False, type(expr)
