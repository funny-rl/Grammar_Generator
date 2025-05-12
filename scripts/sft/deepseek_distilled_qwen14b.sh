#!/bin/bash

set -x

nproc_per_node=4
project_name="Grammar_Generation"
experiment_name="GRPO_14B_SFT"
save_path="./checkpoints/sft/$project_name/$experiment_name"

shift 2

torchrun --standalone --nnodes=1 --nproc_per_node=$nproc_per_node ./sft_trainer.py\
    data.train_files="./data/GGD/parquet/train.parquet" \
    data.val_files="./data/GGD/parquet/valid.parquet" \
    data.train_batch_size=8 \
    data.micro_batch_size_per_gpu=2 \
    trainer.default_local_dir=$save_path \
    trainer.project_name=$project_name \
    trainer.total_epochs=100 \
    trainer.experiment_name=$experiment_name $@
