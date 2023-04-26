import random
from collections import Counter

from build_expr_from_components_in_reverse_polish_notation import build_expr_from_components_in_reverse_polish_notation
from context_free_grammar_derivation_generator import ContextFreeGrammarDerivationGenerator
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from logging_functions import log_found_candidate_program, log_candidate_program_passes_all_counterexamples_yielding, \
    log_received_counterexample, log_candidate_program_fails_on_a_counterexample


def uniform_random_sampling(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol,
        function_declaration,
        constraint
):
    # Updated from verification oracle
    counterexample_set = set()

    context_free_grammar_derivation_generator = ContextFreeGrammarDerivationGenerator(
        non_terminals,
        terminals,
        non_terminals_to_production_rules
    )

    size = 1
    while True:
        derivations_of_given_size_generated_by_symbol = list(
            context_free_grammar_derivation_generator.get_derivations_of_given_size_generated_by_symbol(start_symbol,
                                                                                                        size,
                                                                                                        Counter()))
        random.shuffle(derivations_of_given_size_generated_by_symbol)

        for derivation in derivations_of_given_size_generated_by_symbol:
            candidate_program = build_expr_from_components_in_reverse_polish_notation(derivation)
            log_found_candidate_program(candidate_program)

            if all((
                    evaluate_z3_candidate_program_on_z3_counterexample(
                        function_declaration,
                        constraint,
                        candidate_program,
                        counterexample
                    )
                    for counterexample in counterexample_set
            )):
                log_candidate_program_passes_all_counterexamples_yielding(candidate_program)

                counterexample = yield candidate_program
                if counterexample is not None:
                    log_received_counterexample(counterexample)

                    counterexample_set.add(counterexample)
            else:
                log_candidate_program_fails_on_a_counterexample(candidate_program)

        size += 1
