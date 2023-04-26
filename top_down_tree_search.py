import logging

from pqdict import pqdict
from z3 import simplify

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import \
    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation
from logging_functions import log_found_candidate_program, log_candidate_program_passes_all_counterexamples_yielding, \
    log_received_counterexample, log_candidate_program_fails_on_a_counterexample


def top_down_enumeration(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol,
        partial_derivation_key=None
):
    if partial_derivation_key is None:
        def partial_derivation_key(partial_derivation):
            nonlocal non_terminals

            number_of_non_terminals = sum(
                (
                    1
                    for component in partial_derivation
                    if component in non_terminals
                )
            )

            return len(partial_derivation), number_of_non_terminals

    partial_derivations_priority_queue = pqdict()
    partial_derivations_priority_queue[(start_symbol,)] = partial_derivation_key((start_symbol,))
    visited_partial_derivations_set = {(start_symbol,)}

    set_of_yielded_programs = set()

    while partial_derivations_priority_queue:
        partial_derivation = partial_derivations_priority_queue.pop()
        logging.debug('partial_derivation: %s', partial_derivation)

        indices_and_non_terminals_in_partial_derivation = [
            (i, component)
            for (i, component) in enumerate(partial_derivation)
            if component in non_terminals
        ]

        for index, non_terminal in indices_and_non_terminals_in_partial_derivation:
            production_rules = non_terminals_to_production_rules[non_terminal]

            for production_rule in production_rules:
                new_partial_derivation_ = []
                for i, component in enumerate(partial_derivation):
                    if i == index:
                        new_partial_derivation_.extend(production_rule)
                    else:
                        new_partial_derivation_.append(component)

                new_partial_derivation = tuple(new_partial_derivation_)
                logging.debug('new_partial_derivation: %s', new_partial_derivation)

                if not any((
                        component in non_terminals
                        for component in new_partial_derivation
                )):
                    logging.debug('no non-terminals')

                    # no non-terminals, construct expression and yield
                    expression = simplify(
                        build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(new_partial_derivation))

                    if expression not in set_of_yielded_programs:
                        set_of_yielded_programs.add(expression)
                        yield expression
                        logging.debug('yielded: %s', expression)
                    else:
                        logging.debug('skipped: %s', expression)
                else:
                    if new_partial_derivation not in visited_partial_derivations_set:
                        logging.debug('contains non-terminals')

                        # contains non-terminals, enqueue
                        partial_derivations_priority_queue[new_partial_derivation] = partial_derivation_key(
                            new_partial_derivation
                        )
                        visited_partial_derivations_set.add(new_partial_derivation)

                        logging.debug('enqueued: %s', new_partial_derivation)


def top_down_tree_search(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol,
        function_declaration,
        constraint,
        partial_derivation_key=None
):
    # Updated from verification oracle
    counterexample_set = set()

    for candidate_program in top_down_enumeration(
            non_terminals,
            terminals,
            non_terminals_to_production_rules,
            start_symbol,
            partial_derivation_key
    ):
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
