from z3 import simplify

from build_expr_ref_from_components_in_reverse_polish_notation import build_expr_ref_from_components_in_reverse_polish_notation
from iterate_components_in_expr_ref_in_reverse_polish_notation import iterate_components_in_expr_ref_in_reverse_polish_notation


def evaluate_z3_expr_ref(z3_expr_ref, input_variables_to_values):
    z3_expr_ref_components = iterate_components_in_expr_ref_in_reverse_polish_notation(
        z3_expr_ref
    )

    rewritten_z3_expr_ref_components = (
        input_variables_to_values[component] if component in input_variables_to_values else component
        for component in z3_expr_ref_components
    )

    rewritten_z3_expr_ref = build_expr_ref_from_components_in_reverse_polish_notation(
        rewritten_z3_expr_ref_components
    )

    return simplify(rewritten_z3_expr_ref)
