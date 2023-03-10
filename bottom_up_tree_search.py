import itertools
from sys import stderr

from sympy import *

from build_expr_from_components_in_reverse_polish_notation import build_expr_from_components_in_reverse_polish_notation
from iterate_components_in_expr_in_reverse_polish_notation import iterate_components_in_expr_in_reverse_polish_notation
from recursive_default_dict import RecursiveDefaultDict
from replace_function_declaration_in_constraint_with_candidate_program import replace_function_declaration_in_constraint_with_candidate_program


# https://stackoverflow.com/questions/18503096/python-integer-partitioning-with-given-k-partitions

def split_n_to_sum_of_k_positive_integers(n, k):
    if n < 1:
        return
    else:
        if k < 1:
            return
        elif k == 1:
            yield (n, )
        else:
            for i in range(1, n + 1):
                for right in split_n_to_sum_of_k_positive_integers(n - i, k - 1):
                    yield (i, ) + right


def leaf_expression_size(leaf_expression, terminals):
    return sum(
        (
            component in terminals
            for component in iterate_components_in_expr_in_reverse_polish_notation(leaf_expression)
        )
    )


def bottom_up_tree_search(
    non_terminals,
    terminals,
    production_rules,
    start_symbol,
    function_declaration,
    constraint
):
    # Updated from verification oracle
    counterexample_input_set = set()

    # Initialize leaf_expressions, non_leaf_production_rules
    leaf_expressions = dict()
    non_leaf_production_rules = dict()
    for (non_terminal, production_rules_for_non_terminal) in production_rules.items():
        leaf_expressions_for_non_terminal = set()
        non_leaf_production_rules_for_non_terminal = set()

        for production_rule_for_non_terminal in production_rules_for_non_terminal:
            if any((
                component in non_terminals
                for component in iterate_components_in_expr_in_reverse_polish_notation(production_rule_for_non_terminal)
            )):
                non_leaf_production_rules_for_non_terminal.add(production_rule_for_non_terminal)
            else:
                simplified_leaf_expression = simplify(production_rule_for_non_terminal)
                leaf_expressions_for_non_terminal.add(simplified_leaf_expression)
        
        leaf_expressions[non_terminal] = leaf_expressions_for_non_terminal
        non_leaf_production_rules[non_terminal] = non_leaf_production_rules_for_non_terminal
    
    non_terminals_to_expressions = leaf_expressions.copy()

    non_terminals_to_expression_sizes_to_expressions = RecursiveDefaultDict()
    max_expression_size = 1

    for (non_terminal, leaf_expressions_for_non_terminal) in leaf_expressions.items():
        for leaf_expression in leaf_expressions_for_non_terminal:
            non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size][leaf_expression]  

    while True:
        # Iterate non-leaf rules of non-terminals
        for non_terminal, non_leaf_production_rules_for_non_terminal in non_leaf_production_rules.items():
            for non_leaf_production_rule in non_leaf_production_rules_for_non_terminal:
                print('non_terminal', non_terminal, 'non_leaf_production_rule', non_leaf_production_rule, file=stderr)

                components_in_non_leaf_production_rule = list(iterate_components_in_expr_in_reverse_polish_notation(non_leaf_production_rule))

                indices_and_non_terminals_in_non_leaf_production_rule = [
                    (index, component)
                    for (index, component) in enumerate(components_in_non_leaf_production_rule)
                    if component in non_terminals
                ]

                # Replace all non-terminals in production rule in every possible way given max_expression_size
                for sum_of_k_integers in split_n_to_sum_of_k_positive_integers(max_expression_size, len(indices_and_non_terminals_in_non_leaf_production_rule)):
                    print('\t', 'sum_of_k_integers', sum_of_k_integers, file=stderr)

                    for expressions_for_non_terminals_in_non_leaf_production_rule in itertools.product(*[
                        non_terminals_to_expression_sizes_to_expressions[non_terminal_in_non_leaf_production_rule][expression_size]
                        for (index, non_terminal_in_non_leaf_production_rule), expression_size
                        in zip(indices_and_non_terminals_in_non_leaf_production_rule, sum_of_k_integers)
                    ]):
                        print('\t\t', 'expressions_for_non_terminals_in_non_leaf_production_rule', expressions_for_non_terminals_in_non_leaf_production_rule, file=stderr)

                        components_in_new_non_leaf_production_rule = components_in_non_leaf_production_rule.copy()

                        for (index, non_terminal_in_non_leaf_production_rule), expression_for_non_terminal_in_non_leaf_production_rule in zip(
                            indices_and_non_terminals_in_non_leaf_production_rule,
                            expressions_for_non_terminals_in_non_leaf_production_rule
                        ):
                            components_in_new_non_leaf_production_rule[index] = expression_for_non_terminal_in_non_leaf_production_rule
                        
                        simplified_new_expression = simplify(
                            build_expr_from_components_in_reverse_polish_notation(
                                components_in_new_non_leaf_production_rule
                            )
                        )

                        if simplified_new_expression not in non_terminals_to_expressions[non_terminal]:
                            non_terminals_to_expressions[non_terminal].add(simplified_new_expression)
                            non_terminals_to_expression_sizes_to_expressions[non_terminal][max_expression_size][simplified_new_expression]

        print('non_terminals_to_expression_sizes_to_expressions', non_terminals_to_expression_sizes_to_expressions, file=stderr)

        for candidate_program in non_terminals_to_expression_sizes_to_expressions[start_symbol][max_expression_size]:
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

        max_expression_size += 1
