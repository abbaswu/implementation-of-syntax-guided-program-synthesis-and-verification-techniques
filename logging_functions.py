import logging


def log_found_candidate_program(candidate_program):
    logging.info('Found candidate program: %s', candidate_program)


def log_candidate_program_fails_on_a_counterexample(candidate_program):
    logging.info('Candidate program %s fails on a counterexample', candidate_program)


def log_candidate_program_passes_all_counterexamples_yielding(candidate_program):
    logging.info('Candidate program %s passes all counterexamples, yielding', candidate_program)


def log_received_counterexample(counterexample):
    logging.info('Received counterexample %s', counterexample)
