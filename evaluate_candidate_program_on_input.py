from replace_function_declaration_in_constraint_with_candidate_program import \
    replace_function_declaration_in_constraint_with_candidate_program


def evaluate_candidate_program_on_input(
    function_declaration,
    constraint,
    candidate_program,
    counterexample_input
):
    return replace_function_declaration_in_constraint_with_candidate_program(
        counterexample_input,
        function_declaration,
        constraint,
        candidate_program
    ).subs(counterexample_input)
