#!/bin/bash

set -x

python ./_infer.py \
    model.load_param=True \
    model.load_param_path="./checkpoints/sft/Grammar_Generation/SFT/global_step_120" \
    data.output_path="./checkpoints/sft_pass@1.parquet" \
    data.n_samples=1\
    data.path="./data/labeled_G/parquet/test.parquet" \
    rollout.temperature=0\
    rollout.top_p=1.0

