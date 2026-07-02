# Quick Start Guide

This guide will help you get started with Deep Conformal Alignment (DCA) in under 10 minutes.

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended, but CPU works for small experiments)
- At least 8GB RAM

## Installation (2 minutes)

```bash
# Clone repository
git clone https://github.com/username/deep-conformal-alignment.git
cd deep-conformal-alignment

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Download Data (5 minutes)

```bash
# Download NCT-CRC-HE-100K dataset
wget https://zenodo.org/record/1214456/files/NCT-CRC-HE-100K.zip

# Extract
unzip NCT-CRC-HE-100K.zip -d data/

# Prepare splits
python scripts/prepare_dataset.py \
    --data_dir data/NCT-CRC-HE-100K \
    --output_dir data/processed

# Verify
python scripts/verify_dataset.py --data_dir data/processed
```

## Train DCA (2-3 hours on GPU)

```bash
# Train with default settings
python src/train.py \
    --config configs/default.yaml \
    --data_dir data/processed \
    --output_dir outputs/dca_run1
```

## Evaluate Model (2 minutes)

```bash
# Evaluate on test set
python src/evaluate.py \
    --checkpoint outputs/dca_run1/checkpoints/best_model.pth \
    --data_dir data/processed \
    --output_dir outputs/dca_run1/evaluation
```

## Visualize Results (1 minute)

```bash
# Generate deformation visualizations
python scripts/visualize_deformations.py \
    --checkpoint outputs/dca_run1/checkpoints/best_model.pth \
    --data_dir data/processed \
    --output_dir outputs/dca_run1/visualizations
```

## Quick Experiments

### Train on Limited Data (faster)

```bash
python src/train.py \
    --config configs/default.yaml \
    --data_dir data/processed \
    --data_fraction 0.1 \
    --output_dir outputs/dca_10percent
```

### Compare with Baseline

```bash
# Train ResNet-18 baseline
python src/train.py \
    --config configs/default.yaml \
    --model_name resnet18 \
    --data_dir data/processed \
    --output_dir outputs/resnet18_baseline
```

### Run Ablation Study

```bash
# DCA without conformal loss
python src/train.py \
    --config configs/default.yaml \
    --data_dir data/processed \
    --lambda_conf 0.0 \
    --output_dir outputs/dca_no_conformal
```

## Understanding Output

After training, you will find:

```
outputs/dca_run1/
├── checkpoints/
│   ├── best_model.pth      # Best model on validation set
│   └── last_model.pth       # Final epoch model
├── logs/
│   ├── train.log            # Training logs
│   └── tensorboard/         # TensorBoard logs
├── evaluation/
│   ├── confusion_matrix.pdf # Confusion matrix
│   └── results.json         # Numerical results
└── visualizations/
    ├── deformation_fields.pdf
    └── semantic_adaptation.pdf
```

## Key Configuration Options

Edit `configs/default.yaml` or pass command-line arguments:

```yaml
# Model architecture
model:
  name: dca
  lambda_conf: 1.0          # Conformal energy weight (higher = more conformal)
  lambda_smooth: 0.1        # Smoothness weight (higher = smoother deformations)
  scaling_squaring_steps: 7 # Integration steps (higher = more accurate)

# Training
training:
  batch_size: 32            # Reduce if out of memory
  epochs: 50                # More epochs for better convergence
  learning_rate: 0.001      # Adjust if training unstable
  early_stopping: 10        # Patience for early stopping
```

## Troubleshooting

### Out of Memory

Reduce batch size:
```bash
python src/train.py --config configs/default.yaml --batch_size 16
```

### Slow Training

Use fewer workers or smaller resolution:
```bash
python src/train.py --config configs/default.yaml --num_workers 2
```

### CUDA Not Available

Training will automatically fall back to CPU (slower but functional):
```bash
python src/train.py --config configs/default.yaml --device cpu
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore different hyperparameters in [configs/default.yaml](configs/default.yaml)
3. Run the full experimental suite with `run_all_experiments.py`
4. Visualize learning curves in TensorBoard:
   ```bash
   tensorboard --logdir outputs/dca_run1/logs/tensorboard
   ```

## Getting Help

- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open an issue on GitHub for bugs or questions
- Read the paper for methodological details

## Quick Tips

- Start with 10% of data for quick prototyping
- Use early stopping to avoid overfitting
- Monitor conformal energy in logs to verify geometric constraints
- Compare against ResNet-18 baseline first
- Visualize deformations to understand what the model learns
