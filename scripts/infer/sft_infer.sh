#!/bin/bash

set -x

python ./generation.py \
    model.load_param=True \
    model.load_param_path="./checkpoints/sft/Grammar_Generation/GRPO_14B_SFT/global_step_600" \
    data.n_samples=1\
    rollout.temperature=0\
    rollout.top_p=0.9\

