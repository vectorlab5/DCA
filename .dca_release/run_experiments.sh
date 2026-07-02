#!/bin/bash

# Create logs directory
mkdir -p logs

# Run experiments
echo "Running experiment with 10% data..."
python3 -m src.train --epochs 1 --batch_size 16 --data_fraction 0.1 --save_dir checkpoints/frac_0.1 > logs/frac_0.1.log 2>&1

echo "Running experiment with 20% data..."
python3 -m src.train --epochs 1 --batch_size 16 --data_fraction 0.2 --save_dir checkpoints/frac_0.2 > logs/frac_0.2.log 2>&1

echo "Running experiment with 50% data..."
python3 -m src.train --epochs 1 --batch_size 16 --data_fraction 0.5 --save_dir checkpoints/frac_0.5 > logs/frac_0.5.log 2>&1

echo "Running experiment with 100% data..."
python3 -m src.train --epochs 1 --batch_size 16 --data_fraction 1.0 --save_dir checkpoints/frac_1.0 > logs/frac_1.0.log 2>&1

echo "All experiments completed."
