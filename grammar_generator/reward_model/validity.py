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
    Compute the reward score of the solution string based on the data source and ground truth.
    """
    total_reward = 0.0

    try:
        solution = extract_solution(solution_str=solution_str)
        grammar = ast.literal_eval(solution)

        if set(grammar.keys()) != {"productions", "constraints"}:
            raise ValueError("Invalid grammar format")
        
        if ground_truth != {"productions": [""], "constraints": [""]}:
            if grammar == ground_truth:
                total_reward += 1.0
                raise StopIteration

            testcases, _ = get_testcases(
                grammar=grammar,
                k=10,
                timeout=10,
            )
            validity_score = calculate_validity(
                testcases = testcases,
                gt_grammar = ground_truth,
            )
            total_reward += validity_score
        
        else:
            testcases, _ = get_testcases(
                grammar=grammar,
                k=10,
                timeout=10,
            )
            total_reward += 1.0
                                                                                                                     

    except Exception:
        pass            

    return total_reward                               