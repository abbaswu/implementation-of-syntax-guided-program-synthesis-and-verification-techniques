import sympy
import z3


# https://docs.sympy.org/latest/modules/core.html#module-sympy.core.numbers
# https://docs.sympy.org/latest/modules/logic.html
# https://z3prover.github.io/api/html/z3py_8py_source.html#l03188

def z3_expr_ref_to_sympy_expr(z3_expr_ref_to_sympy_symbols, expr_ref):
    num_args = expr_ref.num_args()
    # Expression with multiple variables
    if num_args:
        assert False
    # Atoms
    else:
        if expr_ref in z3_expr_ref_to_sympy_symbols:
            return z3_expr_ref_to_sympy_symbols[expr_ref]
        elif isinstance(expr_ref, z3.IntNumRef):
            return sympy.Integer(expr_ref.as_string())
        else:
            assert False, type(expr_ref)
