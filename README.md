# Implementation of Syntax Guided Program Synthesis and Verification Techniques

## Requirements

- Unix-like system with the `head`, `tail`, and `grep` commands.
- Jupyter Notebook, with a Python 3 kernel and the following extensions:
  - frozendict
  - matplotlib
  - numpy
  - pandas
  - sympy
  - z3-solver
- GNU `parallel`.

## Replication Instructions

1. Run `run_experiments.sh`. Edit `DURATION`, `NUMBER_OF_RUNS`, `NUMBER_OF_PROCESSES` (number of CPU cores to run GNU `parallel`) as desired. This may take several hours.
2. Run the Jupyter Notebook `exploratory_data_analysis.ipynb` to generate the diagrams. Analyzing the log files generated when running the program synthesis algorithms is a CPU- and IO-bound task, and multiprocessing is beneficial to speed up the process. Edit `NUMBER_OF_PROCESSES` at the top of the Jupyter Notebook as desired.

## Code Structure

### Entry Point

- `main.py`

Usage:

```bash
python main.py --algorithm eusolver --benchmark array_search_2
```

### Program Synthesis Algorithms

- Top-down Tree Search: `from top_down_tree_search import top_down_tree_search`
- Bottom-up Tree Search: `from bottom_up_tree_search import bottom_up_tree_search`
- Uniform Random Sampling: `from uniform_random_sampling import uniform_random_sampling`
- Metropolis-Hastings Sampling: `from metropolis_hastings_sampling import metropolis_hastings_sampling`
- EUsolver: `from eusolver import eusolver`

Usage:

#### Define Context-free Grammar and Constraints

```python
from z3 import *

from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
  iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = Int('Start')
StartBool = Bool('StartBool')
x = Int('x')
y = Int('y')

non_terminals = {Start, StartBool}
terminals = {x, y}
non_terminals_to_production_rules = {
    Start: {
        # x
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(x)),
        # y
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y)),
        # 0
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(0))),
        # 1
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(1))),
        # + Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start + Start)),
        # - Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start - Start)),
        # ite StartBool Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(If(StartBool, Start, Start))),
    },
    StartBool: {
        # and StartBool StartBool
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(And(StartBool, StartBool))),
        # or StartBool StartBool
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Or(StartBool, StartBool))),
        # not StartBool
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Not(StartBool))),
        # <= Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start <= Start)),
        # = Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start == Start)),
        # >= Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start >= Start)),
    }
}
start_symbol = Start

input_variable_list = [x, y]
function_declaration = max2 = Function('max2', IntSort(), IntSort(), IntSort())
constraint = And(max2(x, y) >= x, max2(x, y) >= y, Or(max2(x, y) == x, max2(x, y) == y))
```

#### Initialize Instance

```python
from bottom_up_tree_search import bottom_up_tree_search


algorithm_instance = bottom_up_tree_search(
    non_terminals,
    terminals,
    non_terminals_to_production_rules,
    term_non_terminal,
    predicate_non_terminal,
    function_declaration,
    constraint
)
```

### Verification Oracle

- `verification_oracle.py`

#### Initialize Instance

```python
from verification_oracle import verification_oracle

verification_oracle_instance = verification_oracle(
    input_variable_list,
    benchmark.function_declaration,
    benchmark.constraint
)

next(verification_oracle_instance)
```

### Converting z3 `expr_ref`'s to and from components and doing manipulation on them

- `iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation.py`
- `build_z3_expr_ref_from_z3_components_in_reverse_polish_notation.py`
- `evaluate_z3_expr_ref.py`
- `evaluate_z3_candidate_program_on_z3_counterexample.py`
- `replace_z3_function_declaration_in_z3_constraint_with_z3_candidate_program.py`
- `rewrite_z3_candidate_program.py`
- `find_subderivation_rooted_at_index_in_derivation.py`
