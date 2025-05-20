from prompts.base_instruction_dict_format import get_instruction_func, replace_description

def infer_dataset(
        model_name: str,
        data_path: str,
    ):
    import os
    from datasets import load_dataset
    
    jsonl_path = os.path.join(data_path, 'jsonl')
    parquet_path = os.path.join(data_path, 'parquet')
    dataset = load_dataset(
        "json",
        data_files={
            "test": f"{jsonl_path}/test.jsonl",
        }
    )
    test_dataset = dataset['test']
    
    instruction_func = get_instruction_func(model_name)

    def make_map_fn(split):
        def process_fn(example, idx):
            desc = replace_description(example["description"])
            chat_prompt = instruction_func(desc, model_name)
            data = {
                "prompt": chat_prompt,
                "extra_info": {
                    'split': split,
                    'index': idx
                }
            }
            return data
        return process_fn
    
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True)
    test_dataset.to_parquet(os.path.join(parquet_path, 'test.parquet'))

