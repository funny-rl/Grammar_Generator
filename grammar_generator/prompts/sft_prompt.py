from prompts.base_instruction import get_instruction_func, replace_description

def sft_dataset(
        model_name: str,
        data_path: str,
    ):
    import os
    import json
    from datasets import load_dataset
    
    jsonl_path = os.path.join(data_path, 'jsonl')
    parquet_path = os.path.join(data_path, 'parquet')
    
    dataset = load_dataset(
        "json",
        data_files={
            "train": f"{jsonl_path}/train.jsonl",
            "valid": f"{jsonl_path}/valid.jsonl"
        }
    )

    train_dataset = dataset['train']
    valid_dataset = dataset["valid"]
    
    instruction_func = get_instruction_func(model_name)
    
    def list2strings(data):
        strs_data = ','.join(map(lambda item: f'{item}', data))
        return strs_data

    def make_map_fn(split):
        def process_fn(example, idx):
            desc = replace_description(example["description"])
            chat_prompt = instruction_func(desc, model_name)
            
            answer = f"Alright, based on the explanation above, the appropriate grammar for the given last <Specification> is as follows. </think> {json.dumps(example['grammar'], ensure_ascii=False)}"
           
            # productions = list2strings(example["grammar"]["productions"])
            # constraints = list2strings(example["grammar"]["constraints"])
            # answer = f"<think></think> <Grammar> {productions} </Grammar> <Constraint> {constraints} </Constraint>"
            
            data = {
                "prompt": chat_prompt,
                "answer": answer,
                "extra_info": {
                    'split': split,
                    'index': idx,
                }
            }
            return data
        return process_fn
    
    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True)
    valid_dataset = valid_dataset.map(function=make_map_fn('valid'), with_indices=True)
    train_dataset.to_parquet(os.path.join(parquet_path, 'train.parquet'))
    valid_dataset.to_parquet(os.path.join(parquet_path, 'valid.parquet'))


