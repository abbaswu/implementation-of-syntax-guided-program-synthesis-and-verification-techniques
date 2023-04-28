from z3 import *

from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
  iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = Int('Start')
StartBool = Bool('StartBool')
x = Int('x')
y = Int('y')
z = Int('z')

non_terminals = {Start, StartBool}
terminals = {x, y, z}
non_terminals_to_production_rules = {
    Start: {
        # x
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(x)),
        # y
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y)),
        # z
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(z)),
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

term_non_terminal = Start
predicate_non_terminal = StartBool

input_variable_list = [x, y, z]
function_declaration = max3 = Function('max3', IntSort(), IntSort(), IntSort(), IntSort())
constraint = And(max3(x, y, z) >= x, max3(x, y, z) >= y, max3(x, y, z) >= z,
                 Or(max3(x, y, z) == x, max3(x, y, z) == y, max3(x, y, z) == z))
