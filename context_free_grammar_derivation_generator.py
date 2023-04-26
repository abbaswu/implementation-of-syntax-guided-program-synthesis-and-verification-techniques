"""
```python
from z3 import *

from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation


z3_S = Int('S')
z3_B = Bool('B')
z3_x = Int('x')
z3_y = Int('y')

z3_non_terminals = { z3_S, z3_B }
z3_terminals = { z3_x, z3_y }
# non_terminals to a set of tuples containing the production rule in reverse polish notation
z3_non_terminals_to_production_rules = {
  z3_S: {
    # x
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_x)),
    # y
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_y)),
    # 0
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(0))),
    # 1
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(1))),
    # + S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S + z3_S)),
    # - S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S - z3_S)),
    # ite B S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(If(z3_B, z3_S, z3_S))),
  },
  z3_B: {
    # and B B
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(And(z3_B, z3_B))),
    # or B B
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Or(z3_B, z3_B))),
    # not B
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Not(z3_B))),
    # <= S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S <= z3_S)),
    # = S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S == z3_S)),
    # >= S S
    tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S >= z3_S)),
  }
}
z3_start_symbol = z3_S

context_free_grammar_derivation_generator = ContextFreeGrammarDerivationGenerator(
    z3_non_terminals,
    z3_terminals,
    z3_non_terminals_to_production_rules
)

it = get_derivations_of_max_size_generated_by_symbol(z3_start_symbol, 7)
```
"""

import itertools
import random
from collections import Counter, defaultdict
from functools import partial


class ContextFreeGrammarDerivationGenerator:
    __slots__ = (
        'non_terminals',
        'terminals',
        'non_terminals_to_production_rules',
        'symbols_to_sizes_to_generated_derivations',
        'production_rules_to_sizes_to_generated_derivations',
        'generated_derivations_to_non_terminals'
    )

    def __init__(self, non_terminals, terminals, non_terminals_to_production_rules):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.non_terminals_to_production_rules = non_terminals_to_production_rules
        self.symbols_to_sizes_to_generated_derivations = defaultdict(partial(defaultdict, list))
        self.production_rules_to_sizes_to_generated_derivations = defaultdict(partial(defaultdict, list))
        self.generated_derivations_to_non_terminals = dict()

    def get_random_derivation(
            self,
            non_terminal
    ):
        random_derivation = []

        randomly_selected_production_rule = random.choice(self.non_terminals_to_production_rules[non_terminal])
        for symbol in randomly_selected_production_rule:
            if symbol in self.non_terminals:
                random_derivation.extend(self.get_random_derivation(symbol))
            else:
                random_derivation.append(symbol)

        return tuple(random_derivation)

    def get_derivations_of_given_size_generated_by_symbol(
            self,
            symbol,
            size,
            non_terminals_to_number_of_recursions
    ):
        assert size

        # cache hit
        if symbol in self.symbols_to_sizes_to_generated_derivations and size in \
                self.symbols_to_sizes_to_generated_derivations[symbol]:
            yield from self.symbols_to_sizes_to_generated_derivations[symbol][size]
        # cache miss
        else:
            # initialize self.symbols_to_sizes_to_generated_derivations[symbol][size]
            self.symbols_to_sizes_to_generated_derivations[symbol].__getitem__(size)

            # symbol is a non-terminal
            if symbol in self.non_terminals:
                # modify non_terminals_to_number_of_recursions
                non_terminals_to_number_of_recursions[symbol] += 1

                # check recursion_limit
                # we do not expand symbol if recursion_limit is exceeded
                recursion_limit = len(self.non_terminals) * (1 + size)

                if non_terminals_to_number_of_recursions[symbol] > recursion_limit:
                    pass
                else:
                    # for each production_rule, update:
                    # self.symbols_to_sizes_to_generated_derivations
                    # self.generated_derivations_to_symbols
                    for production_rule in self.non_terminals_to_production_rules[symbol]:
                        for derivation in self.get_derivations_of_given_size_generated_by_production_rule(
                                production_rule,
                                size,
                                non_terminals_to_number_of_recursions.copy()
                        ):
                            self.symbols_to_sizes_to_generated_derivations[symbol][size].append(
                                derivation
                            )
                            self.generated_derivations_to_non_terminals[derivation] = symbol
                            yield derivation
            # symbol is a terminal or something else
            else:
                # requires size to be 1
                # stores itself as a 1-tuple in symbols_to_sizes_to_generated_tuples
                if size == 1:
                    derivation = (symbol,)
                    self.symbols_to_sizes_to_generated_derivations[symbol][size].append(
                        derivation
                    )
                    yield derivation

    def get_derivations_of_given_size_generated_by_production_rule(
            self,
            production_rule,
            size,
            non_terminals_to_number_of_recursions
    ):
        assert len(production_rule) and size

        # cache hit
        if production_rule in self.production_rules_to_sizes_to_generated_derivations and size in \
                self.production_rules_to_sizes_to_generated_derivations[production_rule]:
            yield from self.production_rules_to_sizes_to_generated_derivations[production_rule][size]
        # cache miss
        else:
            # initialize self.production_rules_to_sizes_to_generated_derivations[production_rule][size]
            self.production_rules_to_sizes_to_generated_derivations[production_rule].__getitem__(size)

            # split production_rule
            first_symbol, remaining_symbols_tuple = production_rule[0], production_rule[1:]

            # remaining_symbols_tuple empty
            if not remaining_symbols_tuple:
                for derivation in self.get_derivations_of_given_size_generated_by_symbol(
                        first_symbol,
                        size,
                        non_terminals_to_number_of_recursions.copy()
                ):
                    self.production_rules_to_sizes_to_generated_derivations[production_rule][size].append(
                        derivation
                    )
                    yield derivation
            # remaining_symbols_tuple not empty
            else:
                for size_of_first_symbol in range(1, size):
                    list_of_tuples_generated_by_first_symbol = list(
                        self.get_derivations_of_given_size_generated_by_symbol(
                            first_symbol,
                            size_of_first_symbol,
                            non_terminals_to_number_of_recursions.copy()
                        )
                    )

                    size_of_remaining_symbols_tuple = size - size_of_first_symbol
                    list_of_tuples_generated_by_remaining_symbols_tuple = list(
                        self.get_derivations_of_given_size_generated_by_production_rule(
                            remaining_symbols_tuple,
                            size_of_remaining_symbols_tuple,
                            non_terminals_to_number_of_recursions.copy()
                        )
                    )

                    for tuple_generated_by_first_symbol, tuple_generated_by_remaining_symbols_tuple in itertools.product(
                            list_of_tuples_generated_by_first_symbol,
                            list_of_tuples_generated_by_remaining_symbols_tuple
                    ):
                        derivation = tuple_generated_by_first_symbol + tuple_generated_by_remaining_symbols_tuple
                        self.production_rules_to_sizes_to_generated_derivations[production_rule][size].append(
                            derivation
                        )
                        yield derivation

    def get_derivations_of_max_size_generated_by_symbol(self, symbol, max_size):
        for size in range(1, max_size + 1):
            yield from self.get_derivations_of_given_size_generated_by_symbol(symbol, size, Counter())


if __name__ == '__main__':
    from z3 import *

    from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
        iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

    z3_S = Int('S')
    z3_B = Bool('B')
    z3_x = Int('x')
    z3_y = Int('y')

    z3_non_terminals = {z3_S, z3_B}
    z3_terminals = {z3_x, z3_y}
    # non terminals to a set of tuples containing the production rule in reverse polish notation
    z3_non_terminals_to_production_rules = {
        z3_S: [
            # x
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_x)),
            # y
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_y)),
            # 0
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(0))),
            # 1
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(1))),
            # + S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S + z3_S)),
            # - S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S - z3_S)),
            # ite B S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(If(z3_B, z3_S, z3_S))),
        ],
        z3_B: [
            # and B B
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(And(z3_B, z3_B))),
            # or B B
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Or(z3_B, z3_B))),
            # not B
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Not(z3_B))),
            # <= S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S <= z3_S)),
            # = S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S == z3_S)),
            # >= S S
            tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z3_S >= z3_S)),
        ]
    }
    z3_start_symbol = z3_S

    context_free_grammar_derivation_generator = ContextFreeGrammarDerivationGenerator(
        z3_non_terminals,
        z3_terminals,
        z3_non_terminals_to_production_rules
    )

    for i in range(10):
        print(context_free_grammar_derivation_generator.get_random_derivation(z3_S))

    it = context_free_grammar_derivation_generator.get_derivations_of_max_size_generated_by_symbol(z3_start_symbol, 7)
    while True:
        print(next(it))
