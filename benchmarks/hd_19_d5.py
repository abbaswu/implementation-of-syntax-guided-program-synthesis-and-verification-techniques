from z3 import *


# (define-fun hd19 ((x (BitVec 32)) (m (BitVec 32)) (k (BitVec 32))) (BitVec 32)
#   (bvxor x (bvxor (bvshl (bvand (bvxor (bvlshr x k) x) m) k) (bvand (bvxor (bvlshr x k) x) m))))
def hd19(x, m, k):
    return x ^ (((((LShR(x, k)) ^ x) & m) << k) ^ (((LShR(x, k)) ^ x) & m))


from iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation import \
  iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation

Start = BitVec('Start', 32)
x = BitVec('x', 32)
m = BitVec('m', 32)
k = BitVec('k', 32)

non_terminals = {Start}
terminals = {x, m, k}
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
        # m
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(m)),
        # k
        tuple(iterate_z3_components_in_z3_expr_ref_in_reverse_polish_notation(k)),
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

input_variable_list = [x, m, k]
function_declaration = f = Function('f', BitVecSort(32), BitVecSort(32), BitVecSort(32), BitVecSort(32))
constraint = f(x, m, k) == hd19(x, m, k)
