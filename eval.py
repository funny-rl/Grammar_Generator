# Copyright 2024 Bytedance Ltd. and/or its affiliates
# Licensed under the Apache License, Version 2.0

"""
Offline evaluate the performance of a generated file using reward model and ground truth verifier.
The input is a parquet file that contains N generated sequences and (optional) the ground truth.
"""

import hydra
from verl.utils.fs import copy_to_local
import pandas as pd
import numpy as np
from tqdm import tqdmS
from collections import defaultdict
import ray


@ray.remote
def process_item(file_path, fn_name, reward_kwargs, data_source, response_lst, reward_data):
    import importlib.util
    import sys
    import os

    # Load reward function dynamically
    spec = importlib.util.spec_from_file_location("custom_module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["custom_module"] = module
    spec.loader.exec_module(module)

    raw_fn = getattr(module, fn_name)

    def wrapped_fn(*args, **kwargs):
        return raw_fn(*args, **kwargs, **reward_kwargs, test=True)

    ground_truth = reward_data['ground_truth']
    score_lst = [wrapped_fn(data_source, r, ground_truth) for r in response_lst]
    return data_source, np.mean(score_lst)

@hydra.main(config_path='config', config_name='evaluation', version_base=None)
def main(config):
    local_path = copy_to_local(config.data.path)
    dataset = pd.read_parquet(local_path)
    prompts = dataset[config.data.prompt_key]
    responses = dataset[config.data.response_key]
    data_sources = dataset[config.data.data_source_key]
    reward_model_data = dataset[config.data.reward_model_key]

    total = len(dataset)

    # Initialize Ray
    if not ray.is_initialized():
        ray.init()

    # Get reward function config
    reward_fn_config = config.get("custom_reward_function") or {}
    file_path = reward_fn_config.get("path")
    fn_name = reward_fn_config.get("name")
    reward_kwargs = dict(reward_fn_config.get("reward_kwargs", {}))

    if not file_path or not fn_name:
        raise ValueError("custom_reward_function path and name must be set in the config.")

    print(f"using customized reward function '{fn_name}' from '{file_path}'")

    # Create remote tasks
    remote_tasks = [
        process_item.remote(file_path, fn_name, reward_kwargs, data_sources[i], responses[i], reward_model_data[i])
        for i in range(total)
    ]

    data_source_reward = defaultdict(list)

    # Process results as they complete
    with tqdm(total=total) as pbar:
        while remote_tasks:
            done_ids, remote_tasks = ray.wait(remote_tasks)
            for result_id in done_ids:
                data_source, score = ray.get(result_id)
                data_source_reward[data_source].append(score)
                pbar.update(1)

    # Aggregate scores
    metric_dict = {}
    for data_source, rewards in data_source_reward.items():
        metric_dict[f'test_score/{data_source}'] = np.mean(rewards)

    print(metric_dict)


if __name__ == '__main__':
    main()