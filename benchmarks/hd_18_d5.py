from z3 import *


def hd18(x):
    return And(Not(BVRedOr((x - BitVecVal(0x00000001, 32)) & x) == BitVecVal(0x1, 1)), BVRedOr(x) == BitVecVal(0x1, 1))


from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
  iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = Bool('Start')
StartBV = BitVec('StartBV', 32)
x = BitVec('x', 32)

non_terminals = {Start, StartBV}
terminals = {x}
non_terminals_to_production_rules = {
    Start: {
        # bvule StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(ULE(StartBV, StartBV))),
        # bvult StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(ULT(StartBV, StartBV))),
        # bvslt StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV < StartBV)),
        # bvsle StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV <= StartBV)),
        # = StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV == StartBV))
    },
    StartBV: {
        # bvnot StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(~StartBV)),
        # bvxor StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV ^ StartBV)),
        # bvand StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV & StartBV)),
        # bvor StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV | StartBV)),
        # bvneg StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(-StartBV)),
        # bvadd StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV + StartBV)),
        # bvmul StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV * StartBV)),
        # bvudiv StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(UDiv(StartBV, StartBV))),
        # bvurem StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(URem(StartBV, StartBV))),
        # bvlshr StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(LShR(StartBV, StartBV))),
        # bvashr StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV >> StartBV)),
        # bvshl StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV << StartBV)),
        # bvsdiv StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV / StartBV)),
        # bvsrem StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV % StartBV)),
        # bvsub StartBV StartBV
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(StartBV - StartBV)),
        # x
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(x))
    }
}
start_symbol = Start

input_variable_list = [x]
function_declaration = f = Function('f', BitVecSort(32), BoolSort())
constraint = f(x) == hd18(x)
