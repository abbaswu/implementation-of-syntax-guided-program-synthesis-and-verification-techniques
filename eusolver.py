import itertools
import logging
from sys import stderr

import numpy as np
from pqdict import pqdict
from z3 import If

from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from evaluate_z3_expr_ref import evaluate_z3_expr_ref
from bottom_up_tree_search import BottomUpEnumeration
from logging_functions import log_found_candidate_program, log_candidate_program_passes_all_counterexamples_yielding, \
    log_received_counterexample, log_candidate_program_fails_on_a_counterexample


def calculate_entropy(
        counterexample_set,
        term_to_covered_counterexample_set_dict
):
    if not len(counterexample_set):
        return 0.

    number_of_counterexamples_covered_by_terms_list = [
        len(covered_counterexample_set & counterexample_set)
        for covered_counterexample_set in term_to_covered_counterexample_set_dict.values()
    ]

    probabilities_of_counterexamples_labeled_by_terms_ndarray = np.zeros((
        len(counterexample_set), len(term_to_covered_counterexample_set_dict)
    ))
    for i, counterexample in enumerate(counterexample_set):
        # Fill row (with add one smoothing)
        original_row_sum = 0

        for j, (term, covered_counterexample_set) in enumerate(term_to_covered_counterexample_set_dict.items()):
            if counterexample in covered_counterexample_set:
                original_row_sum += number_of_counterexamples_covered_by_terms_list[j]
                probabilities_of_counterexamples_labeled_by_terms_ndarray[i, j] = \
                    number_of_counterexamples_covered_by_terms_list[j] + 1
            else:
                probabilities_of_counterexamples_labeled_by_terms_ndarray[i, j] = 1

        # Normalize row (with add one smoothing)
        probabilities_of_counterexamples_labeled_by_terms_ndarray[i, :] /= (
                original_row_sum + len(term_to_covered_counterexample_set_dict))

    # Calculate the (equally weighted) sum of all rows, and normalize
    probabilities_of_terms_labeling_any_counterexample = np.sum(
        probabilities_of_counterexamples_labeled_by_terms_ndarray, axis=0)
    probabilities_of_terms_labeling_any_counterexample /= np.sum(
        probabilities_of_terms_labeling_any_counterexample)

    # Calculate entropy
    entropy = -np.sum(probabilities_of_terms_labeling_any_counterexample * np.log2(
        probabilities_of_terms_labeling_any_counterexample))

    return entropy


def calculate_information_gain(
        predicate,
        counterexample_set,
        term_to_covered_counterexample_set_dict,
        predicate_to_covered_counterexample_set_dict
):
    if len(counterexample_set):
        covered_counterexample_set = predicate_to_covered_counterexample_set_dict[predicate]
        remaining_counterexample_set = counterexample_set - covered_counterexample_set

        return (len(covered_counterexample_set) * calculate_entropy(covered_counterexample_set,
                                                                    term_to_covered_counterexample_set_dict) + len(
            remaining_counterexample_set) * calculate_entropy(remaining_counterexample_set,
                                                              term_to_covered_counterexample_set_dict)) / len(
            counterexample_set)
    else:
        return 0.


class NotEnoughTermsException(Exception):
    pass


class NotEnoughPredicatesException(Exception):
    pass


def eusolver(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        term_non_terminal,
        predicate_non_terminal,
        function_declaration,
        constraint
):
    bottom_up_enumeration = BottomUpEnumeration(non_terminals, terminals, non_terminals_to_production_rules)
    term_size = 1
    predicate_size = 1

    # Updated from verification oracle
    counterexample_set = set()

    term_to_covered_counterexample_set_dict = dict()
    predicate_set = set()
    predicate_to_covered_counterexample_set_dict = dict()

    def generate_new_term():
        nonlocal term_non_terminal, function_declaration, constraint, bottom_up_enumeration, term_size, term_to_covered_counterexample_set_dict, counterexample_set

        # Generate new term
        while True:
            generated_term_set = bottom_up_enumeration.get_expressions_generated_by_non_terminal_of_given_size(
                term_non_terminal, term_size)
            term_size += 1
            if generated_term_set:
                break

        # Update term_to_covered_counterexample_set_dict
        for term in generated_term_set:
            covered_counterexample_set = set()
            for counterexample in counterexample_set:
                if evaluate_z3_candidate_program_on_z3_counterexample(
                        function_declaration,
                        constraint,
                        term,
                        counterexample
                ):
                    covered_counterexample_set.add(counterexample)

            term_to_covered_counterexample_set_dict[term] = covered_counterexample_set

    def generate_new_predicate():
        nonlocal predicate_non_terminal, function_declaration, constraint, bottom_up_enumeration, predicate_size, predicate_set, predicate_to_covered_counterexample_set_dict, counterexample_set

        # Generate new predicate (excluding True and False)
        while True:
            generated_predicate_set = bottom_up_enumeration.get_expressions_generated_by_non_terminal_of_given_size(
                predicate_non_terminal, predicate_size)
            predicate_size += 1

            filtered_generated_predicate_set = {
                predicate
                for predicate in generated_predicate_set
                if predicate not in (True, False)
            }

            if filtered_generated_predicate_set:
                break

        for predicate in filtered_generated_predicate_set:
            # Add to predicate_set
            predicate_set.add(predicate)

            # Update predicate_to_covered_counterexample_set_dict
            covered_counterexample_set = set()
            for counterexample in counterexample_set:
                if evaluate_z3_expr_ref(
                        predicate,
                        counterexample
                ):
                    covered_counterexample_set.add(counterexample)

            predicate_to_covered_counterexample_set_dict[predicate] = covered_counterexample_set

    def accept_counterexample(counterexample):
        nonlocal function_declaration, constraint, term_to_covered_counterexample_set_dict, counterexample_set

        counterexample_set.add(counterexample)

        for term, covered_counterexample_set in term_to_covered_counterexample_set_dict.items():
            if evaluate_z3_candidate_program_on_z3_counterexample(
                    function_declaration,
                    constraint,
                    term,
                    counterexample
            ):
                covered_counterexample_set.add(counterexample)

        for predicate, covered_counterexample_set in predicate_to_covered_counterexample_set_dict.items():
            if evaluate_z3_expr_ref(
                    predicate,
                    counterexample
            ):
                covered_counterexample_set.add(counterexample)

    def construct_decision_tree(
            counterexample_set,
            term_to_covered_counterexample_set_dict,
            predicate_set,
            predicate_to_covered_counterexample_set_dict
    ):
        logging.debug('construct_decision_tree %s %s %s %s', counterexample_set,
                      term_to_covered_counterexample_set_dict,
                      predicate_set, predicate_to_covered_counterexample_set_dict)

        terms_covering_all_counterexamples = []

        for term, covered_counterexample_set in term_to_covered_counterexample_set_dict.items():
            if counterexample_set.issubset(covered_counterexample_set):
                terms_covering_all_counterexamples.append(term)

        if terms_covering_all_counterexamples:
            return terms_covering_all_counterexamples

        if set().union(*term_to_covered_counterexample_set_dict.values()) != counterexample_set:
            logging.debug('set().union(*term_to_covered_counterexample_set_dict.values()) != input_set')
            raise NotEnoughTermsException

        filtered_predicates_set = {
            predicate for predicate, covered_counterexample_set in predicate_to_covered_counterexample_set_dict.items()
            if covered_counterexample_set and covered_counterexample_set != counterexample_set
        }

        if not filtered_predicates_set:
            logging.debug('not filtered_predicates_set')
            raise NotEnoughPredicatesException

        predicates_priority_queue = pqdict()
        for predicate in filtered_predicates_set:
            predicates_priority_queue[predicate] = calculate_information_gain(
                predicate,
                counterexample_set,
                term_to_covered_counterexample_set_dict,
                predicate_to_covered_counterexample_set_dict
            )

        logging.debug('predicates_priority_queue: %s', predicates_priority_queue)

        constructed_decision_trees = []

        predicate = predicates_priority_queue.pop()

        logging.debug('predicate: %s', predicate)

        left_subtree_counterexample_set = predicate_to_covered_counterexample_set_dict[predicate].copy()

        left_subtree_term_to_covered_counterexample_set_dict = {
            term: left_subtree_counterexample_set & covered_counterexample_set
            for term, covered_counterexample_set
            in term_to_covered_counterexample_set_dict.items()
        }

        left_subtree_predicate_set = filtered_predicates_set - {predicate}

        left_subtree_predicate_to_covered_counterexample_set_dict = {
            left_subtree_predicate: left_subtree_counterexample_set & predicate_to_covered_counterexample_set_dict[
                left_subtree_predicate]
            for left_subtree_predicate in left_subtree_predicate_set
        }

        logging.debug('left_subtree_counterexample_set: %s', left_subtree_counterexample_set)
        logging.debug('left_subtree_term_to_covered_counterexample_set_dict: %s',
                      left_subtree_term_to_covered_counterexample_set_dict)
        logging.debug('left_subtree_predicate_set: %s', left_subtree_predicate_set)
        logging.debug('left_subtree_predicate_to_covered_counterexample_set_dict: %s',
                      left_subtree_predicate_to_covered_counterexample_set_dict)

        left_subtrees = construct_decision_tree(
            left_subtree_counterexample_set,
            left_subtree_term_to_covered_counterexample_set_dict,
            left_subtree_predicate_set,
            left_subtree_predicate_to_covered_counterexample_set_dict
        )

        right_subtree_counterexample_set = counterexample_set - predicate_to_covered_counterexample_set_dict[
            predicate]

        right_subtree_term_to_covered_counterexample_set_dict = {
            term: right_subtree_counterexample_set & covered_counterexample_set_dict
            for term, covered_counterexample_set_dict
            in term_to_covered_counterexample_set_dict.items()
        }

        right_subtree_predicate_set = filtered_predicates_set - {predicate}

        right_subtree_predicate_to_covered_counterexample_set_dict = {
            right_subtree_predicate: right_subtree_counterexample_set &
                                     predicate_to_covered_counterexample_set_dict[right_subtree_predicate]
            for right_subtree_predicate in right_subtree_predicate_set
        }

        logging.debug('right_subtree_counterexample_set: %s', right_subtree_counterexample_set)
        logging.debug('right_subtree_term_to_covered_counterexample_set_dict: %s',
                      right_subtree_term_to_covered_counterexample_set_dict)
        logging.debug('right_subtree_predicate_set: %s', right_subtree_predicate_set)
        logging.debug('right_subtree_predicate_to_covered_counterexample_set_dict: %s',
                      right_subtree_predicate_to_covered_counterexample_set_dict)

        right_subtrees = construct_decision_tree(
            right_subtree_counterexample_set,
            right_subtree_term_to_covered_counterexample_set_dict,
            right_subtree_predicate_set,
            right_subtree_predicate_to_covered_counterexample_set_dict
        )

        for left_subtree, right_subtree in itertools.product(left_subtrees, right_subtrees):
            decision_tree = If(predicate, left_subtree, right_subtree)
            logging.debug('decision_tree: %s', decision_tree)
            # yield decision_tree
            constructed_decision_trees.append(decision_tree)

        return constructed_decision_trees

    generate_new_term()
    while set().union(*term_to_covered_counterexample_set_dict.values()) != counterexample_set:
        generate_new_term()

    while True:
        logging.debug('counterexample_set: %s', counterexample_set)
        logging.debug('term_to_covered_counterexample_set_dict: %s', term_to_covered_counterexample_set_dict)
        logging.debug('predicate_to_covered_counterexample_set_dict: %s', predicate_to_covered_counterexample_set_dict)

        try:
            constructed_decision_trees = construct_decision_tree(
                counterexample_set.copy(),
                term_to_covered_counterexample_set_dict.copy(),
                predicate_set.copy(),
                predicate_to_covered_counterexample_set_dict.copy()
            )
            for decision_tree in constructed_decision_trees:
                log_found_candidate_program(decision_tree)

                if all((
                        evaluate_z3_candidate_program_on_z3_counterexample(
                            function_declaration,
                            constraint,
                            decision_tree,
                            counterexample
                        )
                        for counterexample in counterexample_set
                )):
                    log_candidate_program_passes_all_counterexamples_yielding(decision_tree)

                    counterexample = yield decision_tree
                    if counterexample is not None:
                        log_received_counterexample(counterexample)

                        accept_counterexample(counterexample)
                else:
                    log_candidate_program_fails_on_a_counterexample(decision_tree)

        except NotEnoughPredicatesException:
            logging.debug('NotEnoughPredicatesException')
            generate_new_predicate()
        except NotEnoughTermsException:
            logging.debug('NotEnoughTermsException')
            generate_new_term()
