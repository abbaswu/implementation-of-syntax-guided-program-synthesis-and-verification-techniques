import itertools
from sys import stderr

from z3 import simplify

from build_z3_expr_ref_from_z3_components_in_reverse_polish_notation import build_z3_expr_ref_from_z3_components_in_reverse_polish_notation
from evaluate_z3_candidate_program_on_z3_counterexample import evaluate_z3_candidate_program_on_z3_counterexample
from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation
from recursive_default_dict import RecursiveDefaultDict


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


def z3_bottom_up_enumeration(
    non_terminals,
    terminals,
    production_rules,
    start_symbol
):
    # Initialize leaf_expressions, non_leaf_production_rules
    leaf_expressions = dict()
    non_leaf_production_rules = dict()
    for (non_terminal, production_rules_for_non_terminal) in production_rules.items():
        leaf_expressions_for_non_terminal = set()
        non_leaf_production_rules_for_non_terminal = set()

        for production_rule_for_non_terminal in production_rules_for_non_terminal:
            if any((
                    component in non_terminals
                    for component in production_rule_for_non_terminal
            )):
                non_leaf_production_rules_for_non_terminal.add(production_rule_for_non_terminal)
            else:
                leaf_expression = simplify(
                    build_z3_expr_ref_from_z3_components_in_reverse_polish_notation(
                        production_rule_for_non_terminal
                    )
                )
                leaf_expressions_for_non_terminal.add(leaf_expression)

        leaf_expressions[non_terminal] = leaf_expressions_for_non_terminal
        non_leaf_production_rules[non_terminal] = non_leaf_production_rules_for_non_terminal

    # Initialize max_expression_size
    max_expression_size = 1

    # Initialize non_terminals_to_expression_sizes_to_expressions
    non_terminals_to_expression_sizes_to_expressions = RecursiveDefaultDict()

    for (non_terminal, leaf_expressions_for_non_terminal) in leaf_expressions.items():
        for leaf_expression in leaf_expressions_for_non_terminal:
            non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size][leaf_expression]

    # Initialize non_terminals_to_expressions
    non_terminals_to_expressions = leaf_expressions.copy()

    yield non_terminals_to_expression_sizes_to_expressions[start_symbol][max_expression_size], max_expression_size

    max_expression_size += 1

    while True:
        # Iterate non-leaf rules of non-terminals
        for non_terminal, non_leaf_production_rules_for_non_terminal in non_leaf_production_rules.items():
            for non_leaf_production_rule in non_leaf_production_rules_for_non_terminal:
                # print('non_terminal', non_terminal, 'non_leaf_production_rule', non_leaf_production_rule, file=stderr)

                indices_and_non_terminals_in_non_leaf_production_rule = [
                    (index, component)
                    for (index, component) in enumerate(non_leaf_production_rule)
                    if component in non_terminals
                ]

                # Replace all non-terminals in production rule in every possible way given max_expression_size
                for sum_of_k_integers in split_n_to_sum_of_k_positive_integers(
                        max_expression_size,
                        len(indices_and_non_terminals_in_non_leaf_production_rule)
                ):
                    # print('\t', 'sum_of_k_integers', sum_of_k_integers, file=stderr)

                    for expressions_for_non_terminals_in_non_leaf_production_rule in itertools.product(*[
                        non_terminals_to_expression_sizes_to_expressions[non_terminal_in_non_leaf_production_rule][
                            expression_size]
                        for (index, non_terminal_in_non_leaf_production_rule), expression_size
                        in zip(indices_and_non_terminals_in_non_leaf_production_rule, sum_of_k_integers)
                    ]):
                        # print('\t\t', 'expressions_for_non_terminals_in_non_leaf_production_rule', expressions_for_non_terminals_in_non_leaf_production_rule, file=stderr)

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
                            non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size][
                                new_expression]

            if non_terminal == start_symbol:
                yield non_terminals_to_expression_sizes_to_expressions[non_terminal][
                    max_expression_size], max_expression_size

        max_expression_size += 1


def z3_bottom_up_tree_search(
    non_terminals,
    terminals,
    production_rules,
    start_symbol,
    function_declaration,
    constraint
):
    # Updated from verification oracle
    counterexample_input_set = set()

    for candidate_program_set, candidate_program_size in z3_bottom_up_enumeration(
            non_terminals,
            terminals,
            production_rules,
            start_symbol
    ):
        for candidate_program in candidate_program_set:
            if all((
                    evaluate_z3_candidate_program_on_z3_counterexample(
                        function_declaration,
                        constraint,
                        candidate_program,
                        counterexample_input
                    )
                    for counterexample_input in counterexample_input_set
            )):
                counterexample_input = yield candidate_program
                if counterexample_input is not None:
                    counterexample_input_set.add(counterexample_input)
            else:
                print(f'skipped {candidate_program}')
                pass
