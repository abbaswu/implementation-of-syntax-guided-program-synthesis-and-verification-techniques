import argparse
import logging

from top_down_tree_search import top_down_tree_search
from bottom_up_tree_search import bottom_up_tree_search
from uniform_random_sampling import uniform_random_sampling
from metropolis_hastings_sampling import metropolis_hastings_sampling
from eusolver import eusolver

from benchmarks import max2, max3, array_search_2, array_search_3, hd_01_d5, \
    hd_03_d5, hd_07_d5, hd_09_d5, hd_10_d5, hd_13_d5, hd_18_d5, hd_19_d5, hd_20_d5

from verification_oracle import verification_oracle

algorithm_name_to_algorithm_dict = {
    'top_down_tree_search': top_down_tree_search,
    'bottom_up_tree_search': bottom_up_tree_search,
    'uniform_random_sampling': uniform_random_sampling,
    'metropolis_hastings_sampling': metropolis_hastings_sampling,
    'eusolver': eusolver
}

benchmark_name_to_benchmark_dict = {
    'max2': max2,
    'max3': max3,
    'array_search_2': array_search_2,
    'array_search_3': array_search_3,
    'hd_01_d5': hd_01_d5,
    'hd_03_d5': hd_03_d5,
    'hd_07_d5': hd_07_d5,
    'hd_09_d5': hd_09_d5,
    'hd_10_d5': hd_10_d5,
    'hd_13_d5': hd_13_d5,
    'hd_18_d5': hd_18_d5,
    'hd_19_d5': hd_19_d5,
    'hd_20_d5': hd_20_d5,
}


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--algorithm', required=True, help='algorithm')
    parser.add_argument('--benchmark', required=True, help='benchmark')
    args = parser.parse_args()
    return args.algorithm, args.benchmark


def main():
    algorithm_name, benchmark_name = parse_command_line_arguments()

    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.DEBUG)

    # load algorithm and benchmark
    algorithm = algorithm_name_to_algorithm_dict[algorithm_name]
    benchmark = benchmark_name_to_benchmark_dict[benchmark_name]

    # initialize algorithm_instance
    algorithm_instance = algorithm(
        benchmark.non_terminals,
        benchmark.terminals,
        benchmark.non_terminals_to_production_rules,
        benchmark.start_symbol,
        # benchmark.predicate_non_terminal,
        benchmark.function_declaration,
        benchmark.constraint
    )

    # initialize verification_oracle_instance
    verification_oracle_instance = verification_oracle(benchmark.input_variable_list, benchmark.function_declaration,
                                                       benchmark.constraint)
    next(verification_oracle_instance)

    candidate_program = next(algorithm_instance)

    while True:
        counterexample = verification_oracle_instance.send(candidate_program)

        if counterexample is not None:
            # pdb.set_trace()
            candidate_program = algorithm_instance.send(counterexample)
        else:
            break


if __name__ == '__main__':
    main()
