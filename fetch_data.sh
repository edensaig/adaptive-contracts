#! /bin/bash

data_dir=data

# AlpacaEval
mkdir $data_dir/alpacaeval
alpacaeval_base_url=https://raw.githubusercontent.com/tatsu-lab/alpaca_eval/474386e3be4159b3ebe8f755071e706c47ea7f4f/results/
alpacaeval_evaluator=weighted_alpaca_eval_gpt4_turbo

for m in gpt-3.5-turbo-1106 gpt-4o-mini-2024-07-18 gpt-4o-2024-05-13; do
    echo Fetching results of $m
    url=$alpacaeval_base_url/$m/$alpacaeval_evaluator/annotations.json
    echo URL: $url
    curl -L -o ./$data_dir/alpacaeval/alpacaeval-$m.json $url
    echo
done

# SWE-Bench
mkdir $data_dir/swebench
swebench_base_url=https://raw.githubusercontent.com/SWE-bench/experiments/refs/heads/main/evaluation/bash-only/
for m in 20250807_mini-v1.7.0_gpt-5 20250807_mini-v1.7.0_gpt-5-nano 20250807_mini-v1.7.0_gpt-5-mini 20250807_mini-v1.7.0_gpt-oss-120b 20250726_mini-v1.0.0_o4-mini-2025-04-16 20250726_mini-v1.0.0_o3-2025-04-16; do
    echo Fetching results of $m
    for f in metadata.yaml per_instance_details.json; do
        echo $f
        url=$swebench_base_url/$m/$f
        echo URL: $url
        curl -L -o ./$data_dir/swebench/swebench-$m-$f $url
    done
    echo
done

echo Done!