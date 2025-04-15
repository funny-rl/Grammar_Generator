



import re
import ast

def extract_solution(solution_str):
    solution = re.search("#### (\\-?[0-9\\.\\,]+)", solution_str) # extract the solution after ####
    if solution is None:
        return None
    final_solution = solution.group(0)
    final_solution = final_solution.split('#### ')[1].replace(',', '')
    return final_solution


def compute_score(data_source, solution_str, ground_truth, extra_info = None):
    """compute the reward score of the solution string based on the data source and ground truth.

    Args:
        dtata_source (file type):  ./jsonl
        solution_str ('str'): : Okay, so I have this problem to solve. Let me read it again carefully. The task is to take an integer a, which is b$
tween 1 and 1000, and output something using it. Hmm, but the output isn't immediately clear. Wait, maybe I'm supposed to compute the number of letters in
the English word for that number. That makes sense because it's a common problem where strings are created based on numbers.  
        ground_truth ('dict'):  {'constraints': ['1<=a<=1000'], 'productions': ['<S>->a']}   
        extra_info ('dict'): Defaults to None. -> {'index': 125, 'split': 'train'}  
    Returns:
        _type_: _description_
    """
    if "####" not in solution_str:
        return -2.0 # format reward
    else:
        solution = extract_solution(solution_str)
        if solution is None:
            return -1.5
        gt = ground_truth
        total_reward = 0.0
        
        try:
            solution = ast.literal_eval(solution)
            if isinstance(solution, dict):
                total_reward += 0.5 # format reward
                if len(solution) == 0:
                    total_reward += -0.6 # format reward
                else:
                    total_reward += 0.5 # format reward
                                    
                    correct_key = 0
                    correct_pair = 0
                    
                    num_gt_keys = len(gt)
                    num_sol_keys = len(solution)
                    
                    if num_sol_keys != num_gt_keys:
                        total_reward += -0.5
                    
                    for (GT_key, GT_value) in gt.items():
                        for (S_key, S_value) in solution.items():
                            if S_key == GT_key:
                                correct_key += 1
                                if S_value == GT_value:
                                    correct_pair += 1
                                    break
                    
                    corr_key_ratio =  correct_key / num_gt_keys
                    corr_pair_ratio = correct_pair / num_gt_keys
                    
                    total_reward += corr_key_ratio  # key reward 
                    total_reward += corr_pair_ratio * 5.0 # pair reward
            
        except Exception as e:
            total_reward += -1.0 # format reward
        
        return total_reward      