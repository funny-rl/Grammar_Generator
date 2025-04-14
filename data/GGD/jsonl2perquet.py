
import re

def extract_solution(solution_str):
    solution = re.search("#### (\\-?[0-9\\.\\,]+)", solution_str) # extract the solution after ####
    assert solution is not None
    final_solution = solution.group(0)
    final_solution = final_solution.split('#### ')[1].replace(',', '')
    return final_solution


if __name__ == '__main__':
    import os
    from datasets import load_dataset
    
    jsonl_dir = "./jsonl"
    parquet_dir = "./parquet"
    
    train_jsonl = os.path.join(jsonl_dir, "train.jsonl")
    test_jsonl = os.path.join(jsonl_dir, "test.jsonl")
    
    dataset = load_dataset(jsonl_dir, 'default')
    
    train_dataset = dataset['train']
    test_dataset = dataset["test"]
    
    instruction_following = "Let's think step by step and output the final answer after \"####\"."

    def make_map_fn(split):

        def process_fn(example, idx):
            question = example["description"]
            answer = example["grammar"]
            
            question = question + ' ' + instruction_following
            solution = answer
            
            data = {
                "data_source": jsonl_dir,
                "prompt": [{
                    "role": "user",
                    "content": question
                }],
                "ability": "math",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": solution
                },
                "extra_info": {
                    'split': split,
                    'index': idx
                }
            }
            return data

        return process_fn
    
    
    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True)
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True)
    
    train_dataset.to_parquet(os.path.join(parquet_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(parquet_dir, 'test.parquet'))