from z3 import *

from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
    iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

# (set-logic LIA)
# (synth-fun findIdx ( (y1 Int) (y2 Int) (y3 Int) (k1 Int)) Int ((Start Int ( 0 1 2 3 y1 y2 y3 k1 (ite BoolExpr Start Start))) (BoolExpr Bool ((< Start Start) (<= Start Start) (> Start Start) (>= Start Start)))))
# (declare-var x1 Int)
# (declare-var x2 Int)
# (declare-var x3 Int)
# (declare-var k Int)
# (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (< k x1) (= (findIdx x1 x2 x3 k) 0))))
# (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (> k x3) (= (findIdx x1 x2 x3 k) 3))))
# (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (and (> k x1) (< k x2)) (= (findIdx x1 x2 x3 k) 1))))
# (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (and (> k x2) (< k x3)) (= (findIdx x1 x2 x3 k) 2))))
# (check-synth)

Start = Int('Start')
BoolExpr = Bool('BoolExpr')
y1 = Int('y1')
y2 = Int('y2')
y3 = Int('y3')
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
        # 3
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(IntVal(3))),
        # y1
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y1)),
        # y2
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y2)),
        # y3
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(y3)),
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

input_variable_list = [y1, y2, y3, k1]
function_declaration = findIdx = Function('findIdx', IntSort(), IntSort(), IntSort(), IntSort(), IntSort())
constraint = And(
    # (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (< k x1) (= (findIdx x1 x2 x3 k) 0))))
    Implies(And(y1 < y2, y2 < y3), Implies(k1 < y1, findIdx(y1, y2, y3, k1) == 0)),
    # (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (> k x3) (= (findIdx x1 x2 x3 k) 3))))
    Implies(And(y1 < y2, y2 < y3), Implies(k1 > y3, findIdx(y1, y2, y3, k1) == 3)),
    # (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (and (> k x1) (< k x2)) (= (findIdx x1 x2 x3 k) 1))))
    Implies(And(y1 < y2, y2 < y3), Implies(And(k1 > y1, k1 < y2), findIdx(y1, y2, y3, k1) == 1)),
    # (constraint (=> (and (< x1 x2) (< x2 x3)) (=> (and (> k x2) (< k x3)) (= (findIdx x1 x2 x3 k) 2))))
    Implies(And(y1 < y2, y2 < y3), Implies(And(k1 > y2, k1 < y3), findIdx(y1, y2, y3, k1) == 2))
)
