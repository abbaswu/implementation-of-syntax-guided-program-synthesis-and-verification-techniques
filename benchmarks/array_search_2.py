from z3 import *

from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = Int('Start')
BoolExpr = Bool('BoolExpr')
y1 = Int('y1')
y2 = Int('y2')
k1 = Int('k1')

non_terminals = {Start, BoolExpr}
terminals = {y1, y2, k1}
non_terminals_to_production_rules = {
    Start: {
        # 0
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(0))),
        # 1
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(1))),
        # 2
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(2))),
        # y1
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y1)),
        # y2
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y2)),
        # k1
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(k1)),
        # ite BoolExpr Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(If(BoolExpr, Start, Start))),
    },
    BoolExpr: {
        # < Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start < Start)),
        # <= Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start <= Start)),
        # > Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start > Start)),
        # >= Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start >= Start)),
    }
}
start_symbol = Start
predicate_non_terminal = BoolExpr

input_variable_list = [y1, y2, k1]
function_declaration = findIdx = Function('findIdx', IntSort(), IntSort(), IntSort(), IntSort())
constraint = And(
    Implies(y1 < y2, Implies(k1 < y1, findIdx(y1, y2, k1) == 0)),
    Implies(y1 < y2, Implies(k1 > y2, findIdx(y1, y2, k1) == 2)),
    Implies(y1 < y2, Implies(And(k1 > y1, k1 < y2), findIdx(y1, y2, k1) == 1)),
)
