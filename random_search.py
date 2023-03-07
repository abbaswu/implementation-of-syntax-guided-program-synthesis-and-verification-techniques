import random

from sympy import simplify

from build_expr_from_components_in_reverse_polish_notation import build_expr_from_components_in_reverse_polish_notation
from replace_function_declaration_in_constraint_with_candidate_program import replace_function_declaration_in_constraint_with_candidate_program
from get_get_tuples_of_max_length_generated_by_symbol import get_get_tuples_of_max_length_generated_by_symbol


def random_search(
    non_terminals,
    terminals,
    production_rules,
    start_symbol,
    max_length,
    function_declaration,
    constraint
):
    # Updated from verification oracle
    counterexample_input_set = set()

    get_tuples_of_max_length_generated_by_symbol = get_get_tuples_of_max_length_generated_by_symbol(non_terminals, terminals, production_rules)
    list_of_tuples_generated_by_start_symbol = list(get_tuples_of_max_length_generated_by_symbol(start_symbol, max_length))
    random.shuffle(list_of_tuples_generated_by_start_symbol)

    # print(list_of_tuples_generated_by_start_symbol)
    
    for tuple_generated_by_start_symbol in list_of_tuples_generated_by_start_symbol:
        candidate_program = build_expr_from_components_in_reverse_polish_notation(tuple_generated_by_start_symbol)
        if all((
            replace_function_declaration_in_constraint_with_candidate_program(
                counterexample_input,
                function_declaration,
                constraint,
                candidate_program
            ).subs(counterexample_input)
            for counterexample_input in counterexample_input_set
        )):
            counterexample_input = yield candidate_program
            if counterexample_input is not None:
                counterexample_input_set.add(counterexample_input)
        else:
            print(f'skipped {candidate_program}')
            pass
