import logging
import pdb
from collections import Counter
from itertools import chain
from math import exp
from random import randint, choice, random
from sys import stderr

from z3 import simplify

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import \
    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from context_free_grammar_derivation_generator import ContextFreeGrammarDerivationGenerator
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from find_subderivation_rooted_at_index_in_derivation import find_subderivation_rooted_at_index_in_derivation
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation
from logging_functions import log_found_candidate_program, log_candidate_program_passes_all_counterexamples_yielding, \
    log_received_counterexample, log_candidate_program_fails_on_a_counterexample


def metropolis_hastings_sampling(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol,
        function_declaration,
        constraint
):
    # Updated from verification oracle
    counterexample_input_set = set()

    context_free_grammar_derivation_generator = ContextFreeGrammarDerivationGenerator(
        non_terminals,
        terminals,
        non_terminals_to_production_rules
    )

    size = 1
    while True:
        # get all derivations of the size
        derivations = set(context_free_grammar_derivation_generator.get_derivations_of_given_size_generated_by_symbol(
            start_symbol,
            size,
            Counter()
        ))

        if derivations:
            candidate_programs_to_number_of_wrong_counterexamples = dict()

            def get_number_of_wrong_counterexamples(candidate_program):
                nonlocal candidate_programs_to_number_of_wrong_counterexamples

                if candidate_program not in candidate_programs_to_number_of_wrong_counterexamples:
                    candidate_programs_to_number_of_wrong_counterexamples[candidate_program] = 0
                    for counterexample in counterexample_input_set:
                        if not evaluate_z3_candidate_program_on_z3_counterexample(
                                function_declaration,
                                constraint,
                                candidate_program,
                                counterexample
                        ):
                            candidate_programs_to_number_of_wrong_counterexamples[candidate_program] += 1

                return candidate_programs_to_number_of_wrong_counterexamples[candidate_program]

            def accept_counterexample(counterexample):
                nonlocal counterexample_input_set, candidate_programs_to_number_of_wrong_counterexamples

                if counterexample not in counterexample_input_set:
                    for expression in candidate_programs_to_number_of_wrong_counterexamples:
                        if not evaluate_z3_candidate_program_on_z3_counterexample(
                                function_declaration,
                                constraint,
                                expression,
                                counterexample
                        ):
                            candidate_programs_to_number_of_wrong_counterexamples[expression] += 1

                    counterexample_input_set.add(counterexample)

            # randomly select a derivation
            derivation = derivations.pop()
            candidate_program = simplify(build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(derivation))

            while derivations:
                log_found_candidate_program(candidate_program)

                derivations.discard(derivation)

                candidate_program_number_of_wrong_counterexamples = get_number_of_wrong_counterexamples(candidate_program)

                if candidate_program_number_of_wrong_counterexamples == 0:
                    log_candidate_program_passes_all_counterexamples_yielding(candidate_program)

                    counterexample = yield candidate_program
                    if counterexample is not None:
                        log_received_counterexample(counterexample)

                        accept_counterexample(counterexample)
                else:
                    log_candidate_program_fails_on_a_counterexample(candidate_program)

                # randomly select an index
                index = randint(0, size - 1)

                # find_subderivation_rooted_at_index_in_derivation
                subderivation = find_subderivation_rooted_at_index_in_derivation(derivation, index)
                subderivation_terminal = context_free_grammar_derivation_generator.generated_derivations_to_non_terminals[
                    subderivation]
                subderivation_size = len(subderivation)

                # new_subderivation
                new_subderivation = choice(
                    context_free_grammar_derivation_generator.symbols_to_sizes_to_generated_derivations[
                        subderivation_terminal][subderivation_size])

                new_derivation = tuple(
                    chain(
                        derivation[:(index + 1 - subderivation_size)],
                        new_subderivation,
                        derivation[(index + 1):]
                    )
                )

                new_candidate_program = simplify(build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(new_derivation))

                new_candidate_program_number_of_wrong_counterexamples = get_number_of_wrong_counterexamples(new_candidate_program)

                expression_score = exp(-0.5 * candidate_program_number_of_wrong_counterexamples)
                new_expression_score = exp(-0.5 * new_candidate_program_number_of_wrong_counterexamples)
                acceptance_ratio = min(1., new_expression_score / expression_score)

                logging.debug('%s -> %s: %s', derivation, new_derivation, acceptance_ratio)

                if random() < acceptance_ratio:
                    derivation = new_derivation
                    candidate_program = new_candidate_program

        size += 1
