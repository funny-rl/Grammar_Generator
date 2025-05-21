import ast 
from reward_model.utils import extract_solution, get_testcases


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
        
        
        testcases, methods = get_testcases(
            grammar = grammar,
            k=10,
            timeout = 10,
        )
        total_reward += 1.0 
    except Exception as e:
        pass
    return total_reward