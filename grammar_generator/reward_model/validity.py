import ast
from reward_model.utils import extract_solution, get_testcases

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
            return total_reward  # Invalid format

        # Always test the grammar
        testcases, methods = get_testcases(
            grammar=grammar,
            k=5,
            timeout=10,
        )
        total_reward += 1.0

    except Exception:
        pass  # Silently ignore all errors

    return total_reward