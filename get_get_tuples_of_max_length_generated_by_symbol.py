"""
```python
from sympy import *

from iterate_components_in_expr_in_reverse_polish_notation import iterate_components_in_expr_in_reverse_polish_notation


S = symbols('S')
B = symbols('B')
x = symbols('x')
y = symbols('y')

non_terminals = { S, B }
terminals = { x, y }
# non_terminals to a set of tuples containing the production_rule in reverse_polish_notation
production_rules = {
  S: {
    tuple(iterate_components_in_expr_in_reverse_polish_notation(x)),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(y)),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Add(S, S, evaluate=False))),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Add(S, -S, evaluate=False))),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Piecewise((S, B), (S, True), evaluate=False)))
  },
  B: {
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Le(S, S, evaluate=False))),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Eq(S, S, evaluate=False))),
    tuple(iterate_components_in_expr_in_reverse_polish_notation(Ge(S, S, evaluate=False)))
  }
}
```

```python
In [2]: from get_get_tuples_of_max_length_generated_by_symbol import get_get_tuples_of_max_length_generated_by_symbol

In [3]: get_tuples_of_max_length_generated_by_symbol = get_get_tuples_of_max_length_generated_by_symbol(non_terminals, terminals, pro
   ...: duction_rules)

In [4]: it = get_tuples_of_max_length_generated_by_symbol(S, 7)

In [5]: next(it)
get_tuples_of_given_length_generated_by_symbol(S, 1) cache miss
get_tuples_of_given_length_generated_by_symbol(x, 1) cache miss
get_tuples_of_given_length_generated_by_symbol(y, 1) cache miss
Out[5]: (x,)

In [6]: next(it)
Out[6]: (y,)

In [7]: next(it)
get_tuples_of_given_length_generated_by_symbol(S, 2) cache miss
get_tuples_of_given_length_generated_by_symbol(x, 2) cache miss
get_tuples_of_given_length_generated_by_symbol(y, 2) cache miss
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 3) cache miss
get_tuples_of_given_length_generated_by_symbol(x, 3) cache miss
get_tuples_of_given_length_generated_by_symbol(y, 3) cache miss
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(-1, 1) cache miss
get_tuples_of_given_length_generated_by_symbol(S, 2) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(B, 1) cache miss
get_tuples_of_given_length_generated_by_symbol(S, 2) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol(S, 1) cache hit
get_tuples_of_given_length_generated_by_symbol((<class 'sympy.core.add.Add'>, 2), 1) cache miss
get_tuples_of_given_length_generated_by_symbol(S, 2) cache hit
Out[7]: (x, x, (sympy.core.add.Add, 2))
```
"""

import itertools
from collections import Counter

from recursive_default_dict import RecursiveDefaultDict


# Uses the closure design pattern and returns a function 'get_tuples_of_max_length_generated_by_symbol(symbol, max_length)' instead of using a class.
def get_get_tuples_of_max_length_generated_by_symbol(
    non_terminals,
    terminals,
    production_rules
):
    # Various cache data structures
    symbols_to_lengths_to_cached_generated_tuples = RecursiveDefaultDict()
    tuple_of_symbols_to_lengths_to_cached_generated_tuples = RecursiveDefaultDict()
    non_terminals_to_number_of_recursions = Counter()

    # Internal helper function
    def get_tuples_of_given_length_generated_by_symbol(symbol, length):
        nonlocal symbols_to_lengths_to_cached_generated_tuples, tuple_of_symbols_to_lengths_to_cached_generated_tuples, non_terminals_to_number_of_recursions

        assert length

        # in symbols_to_lengths_to_cached_generated_tuples, cache hit
        if symbol in symbols_to_lengths_to_cached_generated_tuples and length in symbols_to_lengths_to_cached_generated_tuples[symbol]:
            print(f'get_tuples_of_given_length_generated_by_symbol({symbol}, {length}) cache hit')
            pass
        # not in symbols_to_lengths_to_cached_generated_tuples, cache miss
        else:
            print(f'get_tuples_of_given_length_generated_by_symbol({symbol}, {length}) cache miss')
            # symbol is a non_terminal
            if symbol in non_terminals:
                non_terminal = symbol

                non_terminals_to_number_of_recursions[non_terminal] += 1
                recursion_limit = len(non_terminals) * (1 + length)
                
                # exceeds recursion_limit, only select production rules which do not contain left recursion
                if non_terminals_to_number_of_recursions[non_terminal] > recursion_limit:
                    selected_production_rules = { production_rule for production_rule in production_rules[non_terminal] if production_rule[0] != non_terminal }
                # does not exceed recursion_limit, select all production rules
                else:
                    selected_production_rules = production_rules[non_terminal]
                
                # for each selected_production_rule, add to symbols_to_lengths_to_cached_generated_tuples all tuple_of_given_length_generated_by_selected_production_rule
                for selected_production_rule in selected_production_rules:
                    for tuple_of_given_length_generated_by_selected_production_rule in get_tuples_of_given_length_generated_by_tuple_of_symbols(selected_production_rule, length):
                        symbols_to_lengths_to_cached_generated_tuples[symbol][length][tuple_of_given_length_generated_by_selected_production_rule]
            # symbol is a terminal or something else
            else:
                # requires length to be 1
                # stores itself as a 1-tuple in symbols_to_lengths_to_cached_generated_tuples
                if length == 1:
                    symbols_to_lengths_to_cached_generated_tuples[symbol][length][(symbol, )]

        # yield results
        # also initializes symbols_to_lengths_to_cached_generated_tuples[symbol][length] if not initialized
        # print(f'get_tuples_of_given_length_generated_by_symbol({symbol}, {length}) returns {symbols_to_lengths_to_cached_generated_tuples[symbol][length].keys()}')
        yield from symbols_to_lengths_to_cached_generated_tuples[symbol][length].keys()

    # Internal helper function
    def get_tuples_of_given_length_generated_by_tuple_of_symbols(tuple_of_symbols, length):
        nonlocal symbols_to_lengths_to_cached_generated_tuples, tuple_of_symbols_to_lengths_to_cached_generated_tuples, non_terminals_to_number_of_recursions

        assert len(tuple_of_symbols) and length

        # print(f'get_tuples_of_given_length_generated_by_tuple_of_symbols({tuple_of_symbols}, {length})')

        # in tuple_of_symbols_to_lengths_to_cached_generated_tuples, cache hit
        if tuple_of_symbols in tuple_of_symbols_to_lengths_to_cached_generated_tuples and length in tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols]:
            # print('cache hit')
            pass
        # not in tuple_of_symbols_to_lengths_to_cached_generated_tuples, cache miss
        else:
            # print('cache miss')
            # split tuple_of_symbols
            first_symbol, remaining_symbols_tuple = tuple_of_symbols[0], tuple_of_symbols[1:]

            # remaining_symbols_tuple empty
            if not remaining_symbols_tuple:
                for tuple_generated_by_first_symbol in get_tuples_of_given_length_generated_by_symbol(first_symbol, length):
                    tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols][length][tuple_generated_by_first_symbol]
            # remaining_symbols_tuple not empty
            else:
                for length_of_first_symbol in range(1, length):
                    list_of_tuples_generated_by_first_symbol = list(get_tuples_of_given_length_generated_by_symbol(first_symbol, length_of_first_symbol))

                    length_of_remaining_symbols_tuple = length - length_of_first_symbol
                    list_of_tuples_generated_by_remaining_symbols_tuple = list(get_tuples_of_given_length_generated_by_tuple_of_symbols(remaining_symbols_tuple, length_of_remaining_symbols_tuple))

                    # print(f'get_tuples_of_given_length_generated_by_tuple_of_symbols({tuple_of_symbols}, {length})', list_of_tuples_generated_by_first_symbol, list_of_tuples_generated_by_remaining_symbols_tuple)

                    for tuple_generated_by_first_symbol, tuple_generated_by_remaining_symbols_tuple in itertools.product(
                        list_of_tuples_generated_by_first_symbol,
                        list_of_tuples_generated_by_remaining_symbols_tuple
                    ):
                        tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols][length][tuple_generated_by_first_symbol + tuple_generated_by_remaining_symbols_tuple]
        
        # yield results
        # also initializes tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols][length] if not initialized
        # print(f'get_tuples_of_given_length_generated_by_tuple_of_symbols({tuple_of_symbols}, {length}) returns {tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols][length].keys()}')
        yield from tuple_of_symbols_to_lengths_to_cached_generated_tuples[tuple_of_symbols][length].keys()

    # Returned function
    def get_tuples_of_max_length_generated_by_symbol(symbol, max_length):
        nonlocal get_tuples_of_given_length_generated_by_symbol

        for length in range(1, max_length + 1):
            yield from get_tuples_of_given_length_generated_by_symbol(symbol, length)

    return get_tuples_of_max_length_generated_by_symbol
