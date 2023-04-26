import itertools

from collections import defaultdict
from functools import partial

from z3 import simplify

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import \
    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation
from logging_functions import log_found_candidate_program, log_candidate_program_passes_all_counterexamples_yielding, \
    log_received_counterexample, log_candidate_program_fails_on_a_counterexample


# https://stackoverflow.com/questions/18503096/python-integer-partitioning-with-given-k-partitions

def split_n_to_sum_of_k_positive_integers(n, k):
    if n < 1:
        return
    else:
        if k < 1:
            return
        elif k == 1:
            yield (n,)
        else:
            for i in range(1, n + 1):
                for right in split_n_to_sum_of_k_positive_integers(n - i, k - 1):
                    yield (i,) + right


class BottomUpEnumeration:
    __slots__ = (
        'non_terminals',
        'terminals',
        'non_terminals_to_production_rules',
        'non_terminals_to_non_leaf_production_rules',
        'non_terminals_to_expression_sets',
        'non_terminals_to_max_expression_sizes',
        'non_terminals_to_expression_sizes_to_expressions',
        'expressions_to_non_terminals_and_sizes'
    )

    def __init__(
            self,
            non_terminals,
            terminals,
            non_terminals_to_production_rules
    ):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.non_terminals_to_production_rules = non_terminals_to_production_rules

        self.non_terminals_to_non_leaf_production_rules = dict()

        self.non_terminals_to_expression_sets = dict()
        self.non_terminals_to_max_expression_sizes = dict()
        self.non_terminals_to_expression_sizes_to_expressions = defaultdict(partial(defaultdict, list))
        self.expressions_to_non_terminals_and_sizes = dict()

        for (non_terminal, production_rules) in non_terminals_to_production_rules.items():
            leaf_expression_set = set()
            non_leaf_production_rule_set = set()

            for production_rule in production_rules:
                if any((
                        component in non_terminals
                        for component in production_rule
                )):
                    non_leaf_production_rule_set.add(production_rule)
                else:
                    leaf_expression = simplify(
                        build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
                            production_rule
                        )
                    )
                    leaf_expression_set.add(leaf_expression)

            self.non_terminals_to_non_leaf_production_rules[non_terminal] = list(non_leaf_production_rule_set)
            self.non_terminals_to_expression_sets[non_terminal] = leaf_expression_set

        for (non_terminal, leaf_expression_set) in self.non_terminals_to_expression_sets.items():
            self.non_terminals_to_max_expression_sizes[non_terminal] = 1
            self.non_terminals_to_expression_sizes_to_expressions[non_terminal][1] = list(leaf_expression_set)
            for leaf_expression in leaf_expression_set:
                self.expressions_to_non_terminals_and_sizes[leaf_expression] = (non_terminal, 1)

    def get_expressions_generated_by_non_terminal_of_given_size(
            self,
            non_terminal,
            expression_size
    ):
        if expression_size <= self.non_terminals_to_max_expression_sizes[non_terminal]:
            return self.non_terminals_to_expression_sizes_to_expressions[non_terminal][expression_size]
        else:
            for current_expression_size in range(self.non_terminals_to_max_expression_sizes[non_terminal] + 1, expression_size + 1):
                self.non_terminals_to_expression_sizes_to_expressions[non_terminal][current_expression_size] = list()

                for non_leaf_production_rule in self.non_terminals_to_non_leaf_production_rules[non_terminal]:
                    if current_expression_size >= len(non_leaf_production_rule):
                        indices_and_non_terminals_in_non_leaf_production_rule = [
                            (index, component)
                            for (index, component) in enumerate(non_leaf_production_rule)
                            if component in self.non_terminals
                        ]

                        number_of_other_components_in_non_leaf_production_rule = len(
                            non_leaf_production_rule) - len(
                            indices_and_non_terminals_in_non_leaf_production_rule)
                        total_size_of_all_derivations_of_non_terminals_in_non_leaf_production_rule = current_expression_size - number_of_other_components_in_non_leaf_production_rule

                        # Replace all non-terminals in production rule in every possible way
                        for sum_of_k_integers in split_n_to_sum_of_k_positive_integers(
                                total_size_of_all_derivations_of_non_terminals_in_non_leaf_production_rule,
                                len(indices_and_non_terminals_in_non_leaf_production_rule)
                        ):
                            for expressions_for_non_terminals_in_non_leaf_production_rule in itertools.product(
                                    *[
                                        self.get_expressions_generated_by_non_terminal_of_given_size(non_terminal_in_non_leaf_production_rule, subexpression_size)
                                        for (index, non_terminal_in_non_leaf_production_rule), subexpression_size
                                        in zip(indices_and_non_terminals_in_non_leaf_production_rule,
                                               sum_of_k_integers)
                                    ]):

                                new_non_leaf_production_rule = list(non_leaf_production_rule)

                                for (
                                        (index, non_terminal_in_non_leaf_production_rule),
                                        expression_for_non_terminal_in_non_leaf_production_rule
                                ) in zip(
                                    indices_and_non_terminals_in_non_leaf_production_rule,
                                    expressions_for_non_terminals_in_non_leaf_production_rule
                                ):
                                    new_non_leaf_production_rule[
                                        index] = expression_for_non_terminal_in_non_leaf_production_rule

                                new_expression = simplify(
                                    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
                                        new_non_leaf_production_rule
                                    )
                                )

                                if new_expression not in self.non_terminals_to_expression_sets[non_terminal]:
                                    self.non_terminals_to_expression_sets[non_terminal].add(new_expression)
                                    self.non_terminals_to_expression_sizes_to_expressions[non_terminal][
                                        current_expression_size].append(
                                        new_expression
                                    )
                                    self.expressions_to_non_terminals_and_sizes[new_expression] = (non_terminal, current_expression_size)

                self.non_terminals_to_max_expression_sizes[non_terminal] = current_expression_size

            return self.non_terminals_to_expression_sizes_to_expressions[non_terminal][
                expression_size
            ]


def bottom_up_enumeration(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol
):
    # Initialize non_terminals_to_leaf_expressions, non_terminals_to_non_leaf_production_rules, non_leaf_production_rules_to_indices_and_non_terminals
    non_terminals_to_leaf_expressions = dict()
    non_terminals_to_non_leaf_production_rules = dict()

    for (non_terminal, production_rules) in non_terminals_to_production_rules.items():
        leaf_expressions = set()
        non_leaf_production_rules = set()

        for production_rule in production_rules:
            if any((
                    component in non_terminals
                    for component in production_rule
            )):
                non_leaf_production_rules.add(production_rule)
            else:
                leaf_expression = simplify(
                    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
                        production_rule
                    )
                )
                leaf_expressions.add(leaf_expression)

        non_terminals_to_leaf_expressions[non_terminal] = leaf_expressions
        non_terminals_to_non_leaf_production_rules[non_terminal] = non_leaf_production_rules

    # Initialize max_expression_size
    max_expression_size = 1

    # Initialize non_terminals_to_expression_sizes_to_expressions
    non_terminals_to_expression_sizes_to_expressions = defaultdict(partial(defaultdict, set))

    for (non_terminal, leaf_expressions) in non_terminals_to_leaf_expressions.items():
        for leaf_expression in leaf_expressions:
            non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size].add(leaf_expression)

    # Initialize non_terminals_to_expressions
    non_terminals_to_expressions = non_terminals_to_leaf_expressions.copy()

    yield from non_terminals_to_expression_sizes_to_expressions[start_symbol][max_expression_size]

    max_expression_size += 1

    while True:
        # Iterate non-leaf rules of non-terminals
        for non_terminal, non_leaf_production_rules in non_terminals_to_non_leaf_production_rules.items():
            for non_leaf_production_rule in non_leaf_production_rules:
                if max_expression_size >= len(non_leaf_production_rule):
                    indices_and_non_terminals_in_non_leaf_production_rule = [
                        (index, component)
                        for (index, component) in enumerate(non_leaf_production_rule)
                        if component in non_terminals
                    ]

                    number_of_other_components_in_non_leaf_production_rule = len(non_leaf_production_rule) - len(
                        indices_and_non_terminals_in_non_leaf_production_rule)
                    total_size_of_all_derivations_of_non_terminals_in_non_leaf_production_rule = max_expression_size - number_of_other_components_in_non_leaf_production_rule

                    # Replace all non-terminals in production rule in every possible way
                    for sum_of_k_integers in split_n_to_sum_of_k_positive_integers(
                            total_size_of_all_derivations_of_non_terminals_in_non_leaf_production_rule,
                            len(indices_and_non_terminals_in_non_leaf_production_rule)
                    ):
                        for expressions_for_non_terminals_in_non_leaf_production_rule in itertools.product(*[
                            non_terminals_to_expression_sizes_to_expressions[non_terminal_in_non_leaf_production_rule][
                                expression_size]
                            for (index, non_terminal_in_non_leaf_production_rule), expression_size
                            in zip(indices_and_non_terminals_in_non_leaf_production_rule, sum_of_k_integers)
                        ]):

                            new_non_leaf_production_rule = list(non_leaf_production_rule)

                            for (
                                    (index, non_terminal_in_non_leaf_production_rule),
                                    expression_for_non_terminal_in_non_leaf_production_rule
                            ) in zip(
                                indices_and_non_terminals_in_non_leaf_production_rule,
                                expressions_for_non_terminals_in_non_leaf_production_rule
                            ):
                                new_non_leaf_production_rule[
                                    index] = expression_for_non_terminal_in_non_leaf_production_rule

                            new_expression = simplify(
                                build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
                                    new_non_leaf_production_rule
                                )
                            )

                            if new_expression not in non_terminals_to_expressions[non_terminal]:
                                non_terminals_to_expressions[non_terminal].add(new_expression)
                                non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size].add(
                                    new_expression
                                )

                                if non_terminal is start_symbol:
                                    yield new_expression

        max_expression_size += 1


def bottom_up_tree_search(
        non_terminals,
        terminals,
        non_terminals_to_production_rules,
        start_symbol,
        function_declaration,
        constraint
):
    # Updated from verification oracle
    counterexample_set = set()

    for candidate_program in bottom_up_enumeration(
            non_terminals,
            terminals,
            non_terminals_to_production_rules,
            start_symbol
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
