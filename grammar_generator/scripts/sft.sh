#!/bin/bash

set -x

nproc_per_node=4
project_name="SFT"
experiment_name="SFT"
save_path="./checkpoints/sft/$project_name/$experiment_name"
shift 2

torchrun --standalone --nnodes=1 --nproc_per_node=$nproc_per_node ./_sft_trainer.py\
    data.train_files="./data/labeled_G/parquet/train.parquet" \
    data.val_files="./data/labeled_G/parquet/valid.parquet" \
    data.path="./data/labeled_G/" \
    data.train_batch_size=16\
    data.micro_batch_size_per_gpu=2\
    trainer.default_local_dir=$save_path\
    trainer.project_name=$project_name\
    trainer.total_epochs=20\
    trainer.experiment_name=$experiment_name $@