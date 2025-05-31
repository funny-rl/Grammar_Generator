import ast 
import time
from reward_model.utils import extract_solution, get_testcases, calculate_validity


def compute_score(
        data_source, 
        solution_str, 
        ground_truth, 
        extra_info=None,
    ):
    """
    compute the reward score of the solution string based on the data source and ground truth.
    """
    solution = extract_solution(solution_str = solution_str)
    total_reward = 0.0
    try:
        grammar = ast.literal_eval(solution)
        if set(grammar.keys()) != {"productions", "constraints"}:
            raise ValueError("Invalid grammar format")
        
        if grammar == ground_truth:
            total_reward += 1.0
            raise StopIteration
        
        testcases, methods = get_testcases(
            grammar = grammar,
            k=10,
            timeout = 10,
        )
        validity_score = calculate_validity(
            testcases = testcases,
            gt_grammar = ground_truth,
        )
        
        gt_testcases, methods = get_testcases(
            grammar = ground_truth,
            k=10,
            timeout = 10,
        )

        generality_score = calculate_validity(
            testcases = gt_testcases,
            gt_grammar = grammar,
        )
        total_reward += (validity_score * generality_score)
        
    except Exception as e:
        pass
    return total_reward