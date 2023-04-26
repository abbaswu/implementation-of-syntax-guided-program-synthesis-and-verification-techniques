from evaluate_z3_expr_ref import evaluate_z3_expr_ref
from replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program import \
    replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program


def evaluate_z3_candidate_program_on_z3_counterexample(
        z3_function_declaration,
        z3_constraint,
        z3_candidate_program,
        z3_counterexample
):
    return evaluate_z3_expr_ref(
        replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program(
            z3_counterexample,
            z3_function_declaration,
            z3_constraint,
            z3_candidate_program
        ),
        z3_counterexample
    )
