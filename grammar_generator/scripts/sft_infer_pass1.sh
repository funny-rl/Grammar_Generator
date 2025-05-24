#!/bin/bash

set -x

python ./_infer.py \
    model.load_param=True \
    model.load_param_path="./model/sft.pt" \
    data.output_path="./model_output/sft_pass@1.jsonl" \
    data.n_samples=10\
    data.path="./data/labeled_G/parquet/test.parquet" \
    rollout.temperature=0.9\
    rollout.top_p=0.9 \
    rollout.n=1\
