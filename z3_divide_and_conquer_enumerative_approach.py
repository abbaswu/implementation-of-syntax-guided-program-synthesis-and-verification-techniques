import itertools
from sys import stderr

import numpy as np
from z3 import If

from evaluate_z3_expr_ref import evaluate_z3_expr_ref
from z3_bottom_up_tree_search import z3_bottom_up_enumeration
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from recursive_default_dict import RecursiveDefaultDict


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


def z3_divide_and_conquer_enumerative_approach(
        z3_non_terminals,
        z3_terminals,
        z3_production_rules,
        z3_term_non_terminal,
        z3_predicate_non_terminal,
        z3_function_declaration,
        z3_constraint,
        indent_level=0
):
    indent = '    ' * indent_level

    term_iterator = z3_bottom_up_enumeration(z3_non_terminals, z3_terminals, z3_production_rules, z3_term_non_terminal)
    predicate_iterator = z3_bottom_up_enumeration(z3_non_terminals, z3_terminals, z3_production_rules, z3_predicate_non_terminal)

    # Updated from verification oracle
    counterexample_set = set()

    term_to_covered_counterexample_set_dict = dict()
    predicate_set = set()
    predicate_to_covered_counterexample_set_dict = dict()

    def generate_new_term():
        nonlocal z3_function_declaration, z3_constraint, term_iterator, term_to_covered_counterexample_set_dict, counterexample_set

        # Generate new term
        while True:
            generated_term_set, generated_term_size = next(term_iterator)
            if generated_term_set:
                break

        # Update term_to_covered_counterexample_set_dict
        for term in generated_term_set:
            covered_counterexample_set = set()
            for counterexample in counterexample_set:
                if evaluate_z3_candidate_program_on_z3_counterexample(
                    z3_function_declaration,
                    z3_constraint,
                    term,
                    counterexample
                ):
                    covered_counterexample_set.add(counterexample)

            term_to_covered_counterexample_set_dict[term] = covered_counterexample_set

    def generate_new_predicate():
        nonlocal z3_function_declaration, z3_constraint, predicate_iterator, predicate_set, predicate_to_covered_counterexample_set_dict, counterexample_set

        # Generate new predicate (excluding True and False)
        while True:
            generated_predicate_set, generated_predicate_size = next(predicate_iterator)
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
        nonlocal z3_function_declaration, z3_constraint, term_iterator, term_to_covered_counterexample_set_dict, counterexample_set

        counterexample_set.add(counterexample)

        for term, covered_counterexample_set in term_to_covered_counterexample_set_dict.items():
            if evaluate_z3_candidate_program_on_z3_counterexample(
                    z3_function_declaration,
                    z3_constraint,
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
        predicate_to_covered_counterexample_set_dict,
        indent_level=0
    ):
        indent = '    ' * indent_level
        print(indent, 'construct_decision_tree', counterexample_set, term_to_covered_counterexample_set_dict,
              predicate_set, predicate_to_covered_counterexample_set_dict, file=stderr)

        number_of_terms_covering_all_counterexamples = 0

        for term, covered_counterexample_set in term_to_covered_counterexample_set_dict.items():
            if counterexample_set.issubset(covered_counterexample_set):
                print(indent, term, 'covers all counterexamples, yielding', file=stderr)
                number_of_terms_covering_all_counterexamples += 1
                counterexample = yield term

        if number_of_terms_covering_all_counterexamples:
            return

        if set().union(*term_to_covered_counterexample_set_dict.values()) != counterexample_set:
            print(indent,
                  'set().union(*term_to_covered_counterexample_set_dict.values()) != input_set, nothing to yield',
                  file=stderr)
            return

        filtered_predicates_set = {
            predicate for predicate, covered_counterexample_set in predicate_to_covered_counterexample_set_dict.items()
            if covered_counterexample_set and covered_counterexample_set != counterexample_set
        }

        if not filtered_predicates_set:
            print(indent, 'not filtered_predicates_set, nothing to yield', file=stderr)
            return

        remaining_predicates_set = filtered_predicates_set.copy()

        while remaining_predicates_set:
            # Calculating this every time tolerates counterexample_set, term_to_covered_counterexample_set_dict, predicate_to_covered_counterexample_set_dict CHANGING each time a counterexample is added
            predicate_to_information_gain_dict = {
                predicate: calculate_information_gain(
                    predicate,
                    counterexample_set,
                    term_to_covered_counterexample_set_dict,
                    predicate_to_covered_counterexample_set_dict
                )
                for predicate in remaining_predicates_set
            }

            print(indent, 'predicate_to_information_gain_dict:', predicate_to_information_gain_dict, file=stderr)

            predicate = min(
                predicate_to_information_gain_dict.keys(),
                key=lambda predicate: predicate_to_information_gain_dict[predicate]
            )

            remaining_predicates_set.remove(predicate)

            print(indent, 'predicate:', predicate, file=stderr)

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

            print(indent, 'left_subtree_counterexample_set:', left_subtree_counterexample_set, file=stderr)
            print(indent, 'left_subtree_term_to_covered_counterexample_set_dict:',
                  left_subtree_term_to_covered_counterexample_set_dict, file=stderr)
            print(indent, 'left_subtree_predicate_set:', left_subtree_predicate_set, file=stderr)
            print(indent, 'left_subtree_predicate_to_covered_counterexample_set_dict:',
                  left_subtree_predicate_to_covered_counterexample_set_dict, file=stderr)

            left_subtree_set = set(construct_decision_tree(
                left_subtree_counterexample_set,
                left_subtree_term_to_covered_counterexample_set_dict,
                left_subtree_predicate_set,
                left_subtree_predicate_to_covered_counterexample_set_dict,
                indent_level + 1
            ))

            if not left_subtree_set:
                print(indent, 'left_subtree_set is EMPTY, skipping this predicate', file=stderr)
                continue

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

            print(indent, 'right_subtree_counterexample_set:', right_subtree_counterexample_set, file=stderr)
            print(indent, 'right_subtree_term_to_covered_counterexample_set_dict:',
                  right_subtree_term_to_covered_counterexample_set_dict, file=stderr)
            print(indent, 'right_subtree_predicate_set:', right_subtree_predicate_set, file=stderr)
            print(indent, 'right_subtree_predicate_to_covered_counterexample_set_dict:',
                  right_subtree_predicate_to_covered_counterexample_set_dict, file=stderr)

            right_subtree_set = set(construct_decision_tree(
                right_subtree_counterexample_set,
                right_subtree_term_to_covered_counterexample_set_dict,
                right_subtree_predicate_set,
                right_subtree_predicate_to_covered_counterexample_set_dict,
                indent_level + 1
            ))

            if not right_subtree_set:
                print(indent, 'right_subtree_set is EMPTY, skipping this predicate', file=stderr)
                continue

            for left_subtree, right_subtree in itertools.product(left_subtree_set, right_subtree_set):
                decision_tree = If(predicate, left_subtree, right_subtree)
                print(indent, 'yielding', decision_tree, file=stderr)
                yield decision_tree

    generate_new_term()
    while set().union(*term_to_covered_counterexample_set_dict.values()) != counterexample_set:
        generate_new_term()

    generate_new_predicate()

    while True:
        print(indent, 'counterexample_set:', counterexample_set, file=stderr)
        print(indent, 'term_to_covered_counterexample_set_dict:', term_to_covered_counterexample_set_dict, file=stderr)
        print(indent, 'predicate_to_covered_counterexample_set_dict:', predicate_to_covered_counterexample_set_dict,
              file=stderr)

        for decision_tree in construct_decision_tree(
                counterexample_set.copy(),
                term_to_covered_counterexample_set_dict.copy(),
                predicate_set.copy(),
                predicate_to_covered_counterexample_set_dict.copy(),
                indent_level + 1
        ):
            print(indent, 'decision_tree:', decision_tree, file=stderr)
            counterexample = yield decision_tree
            if counterexample is not None:
                print(indent, 'counterexample:', counterexample, file=stderr)
                accept_counterexample(counterexample)
                break
        else:
            print(indent, 'failed to construct decision_tree', file=stderr)

            generate_new_term()
            generate_new_predicate()

            continue
