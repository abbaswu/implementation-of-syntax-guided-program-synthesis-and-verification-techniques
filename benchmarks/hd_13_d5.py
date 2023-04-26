from z3 import *

# (define-fun hd13 ((x (BitVec 32))) (BitVec 32) (bvor (bvashr x #x0000001F) (bvlshr (bvneg x) #x0000001F)))
def hd13(x):
    return (x >> BitVecVal(0x0000001F, 32)) | LShR(-x, BitVecVal(0x0000001F, 32))


from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
  iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = BitVec('Start', 32)
x = BitVec('x', 32)

non_terminals = {Start}
terminals = {x}
non_terminals_to_production_rules = {
    Start: {
        # bvnot Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(~Start)),
        # bvxor Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start ^ Start)),
        # bvand Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start & Start)),
        # bvor Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start | Start)),
        # bvneg Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(-Start)),
        # bvadd Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start + Start)),
        # bvmul Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start * Start)),
        # bvudiv Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(UDiv(Start, Start))),
        # bvurem Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(URem(Start, Start))),
        # bvlshr Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(LShR(Start, Start))),
        # bvashr Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start >> Start)),
        # bvshl Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start << Start)),
        # bvsdiv Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start / Start)),
        # bvsrem Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start % Start)),
        # bvsub Start Start
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(Start - Start)),
        # x
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(x)),
        # #x00000000
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(BitVecVal(0x00000000, 32))),
        # #xFFFFFFFF
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(BitVecVal(0xFFFFFFFF, 32))),
        # #x00000001
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(BitVecVal(0x00000001, 32))),
        # #x0000001F
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(BitVecVal(0x0000001F, 32)))
    }
}
start_symbol = Start

input_variable_list = [x]
function_declaration = f = Function('f', BitVecSort(32), BitVecSort(32))
constraint = f(x) == hd13(x)
