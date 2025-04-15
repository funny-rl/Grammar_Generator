



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
    
    instruction_following = \
    """
        After solving the problem step by step through reasoning, print the answer in Python dictionary format. 
        This dictionary should consist of the keys 'productions' and 'constraints', and the final answer should begin with ####. 
        As an example, if the prompt is 'Input\n\nThe first line contains one integer n (1 <= n <= 15) --- the number of rotations.\n\nEach of the following n lines contains one integer a_i (1 <= a_i <= 180) --- the angle of the i-th rotation in degrees.', 
        then the answer should be ####{'productions': ['<S>->[n] <n> <T_n>', '<T_i>-><T_i-1> <n> a_i', '<T_1>->a_i'], 'constraints': ['1<=n<=15', '1<=a_i<=180']}
    """
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