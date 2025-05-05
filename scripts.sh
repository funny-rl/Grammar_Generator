#!/bin/bash

set -x
# 0508
temperature=0.5
top_p=0.8
batch_size_per_gpu=2
python ./main.py\
    trainer.experiment_name="GRPO_14B_SFT_RL" \
    data.train_files="./data/GGD/parquet/train.parquet" \
    data.val_files="./data/GGD/parquet/valid.parquet" \
    data.max_prompt_length=2450 \
    data.max_response_length=512 \
    data.train_batch_size=16 \
    actor_rollout_ref.actor.ppo_mini_batch_size=8\
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=${batch_size_per_gpu}\
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=16384\
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=${batch_size_per_gpu}\
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=${batch_size_per_gpu}\
    actor_rollout_ref.rollout.temperature=${temperature}\
    actor_rollout_ref.rollout.top_p=${top_p}\
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5\
    actor_rollout_ref.rollout.n=2\
    actor_rollout_ref.rollout.max_num_batched_tokens=8196\
    actor_rollout_ref.rollout.max_num_seqs=1024\
    trainer.save_freq=-1\
    trainer.test_freq=10 \
    trainer.total_epochs=20 \
    trainer.prompt_version="v1"