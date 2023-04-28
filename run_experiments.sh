DURATION=900
NUMBER_OF_RUNS=5
NUMBER_OF_PROCESSES=8


for benchmark in 'array_search_2' 'array_search_3' 'max2' 'max3' 'hd_01_d5' 'hd_03_d5' 'hd_07_d5' 'hd_09_d5' 'hd_10_d5' 'hd_13_d5' 'hd_18_d5' 'hd_19_d5' 'hd_20_d5'
do
    for algorithm in 'top_down_tree_search' 'bottom_up_tree_search' 'metropolis_hastings_sampling' 'uniform_random_sampling'
    do
        log_directory="logs/${benchmark}/${algorithm}"
        mkdir -p "$log_directory"
        
        for i in $(seq 6 1 10)
        do
            log_file="${log_directory}/${i}"
            echo "python main.py --algorithm '${algorithm}' --benchmark '${benchmark}' >'${log_file}'"
        done
    done
done | parallel -j"${NUMBER_OF_PROCESSES}" --verbose --timeout "${DURATION}"


for benchmark in 'array_search_2' 'array_search_3' 'max2' 'max3'
do
    for algorithm in 'eusolver'
    do
        log_directory="logs/${benchmark}/${algorithm}"
        mkdir -p "$log_directory"
        
        for i in $(seq 6 1 10)
        do
            log_file="${log_directory}/${i}"
            echo "python main.py --algorithm '${algorithm}' --benchmark '${benchmark}' >'${log_file}'"
        done
    done
done | parallel -j"${NUMBER_OF_PROCESSES}" --verbose --timeout "${DURATION}"
