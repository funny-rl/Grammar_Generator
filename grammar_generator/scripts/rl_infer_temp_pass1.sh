#!/bin/bash

set -x
#"./checkpoints/rl/Grammar_Generation/Validity_RL/global_step_90/model.pt" 
python ./_infer.py \
    model.load_param=True \
    model.load_param_path="./checkpoints/rl/Grammar_Generation/Validity_RL/global_step_30/model.pt"\
    data.output_path="./model_output/valxgen_pass@1.jsonl" \
    data.n_samples=1\
    data.path="./data/labeled_G/parquet/test.parquet" \
    rollout.temperature=0\
    rollout.top_p=1.0