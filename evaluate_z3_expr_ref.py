from z3 import simplify

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import \
    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation


def evaluate_z3_expr_ref(z3_expr_ref, z3_input_variables_to_values):
    z3_expr_ref_components = iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(
        z3_expr_ref
    )

    rewritten_z3_expr_ref_components = (
        z3_input_variables_to_values[component] if component in z3_input_variables_to_values else component
        for component in z3_expr_ref_components
    )

    rewritten_z3_expr_ref = build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
        rewritten_z3_expr_ref_components
    )

    return simplify(rewritten_z3_expr_ref)
