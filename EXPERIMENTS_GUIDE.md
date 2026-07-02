# Experiment Guide

This document describes how to run all experiments for the DCA paper.

## Quick Start

### Run All Experiments
```bash
python run_all_experiments.py --config configs/default.yaml
```

### Run Individual Experiments

#### 1. Main Comparison (Table 1 in paper)
Compare DCA against all baselines:
```bash
python -m src.experiments.comparison --config configs/default.yaml
```

#### 2. Data Efficiency (Figure 3 in paper)
Evaluate performance with varying training data sizes:
```bash
python -m src.experiments.data_efficiency --config configs/default.yaml
```

#### 3. Ablation Study (Table 2 in paper)
Analyze contribution of each component:
```bash
python -m src.experiments.ablation --config configs/default.yaml
```

#### 4. Hyperparameter Sensitivity (Figure 4 in paper)
Test sensitivity to key hyperparameters:
```bash
python -m src.experiments.hyperparameter --config configs/default.yaml
```

#### 5. Robustness Analysis (Figure 5 in paper)
Test robustness to image perturbations:
```bash
python -m src.experiments.robustness --config configs/default.yaml
```

## Experiment Details

### 1. Main Comparison Experiment

**Models Tested:**
- DCA (our method)
- ResNet-18, ResNet-50
- EfficientNet-B0
- Vision Transformer (ViT-B/16)
- STN-Affine, STN-TPS
- PLIP (linear probe)
- UNI (linear probe)
- CONCH (linear probe)

**Output:**
- `comparison_results.json` - Full results
- `summary_table.csv` - Summary table (Table 1)
- Model checkpoints for each baseline

**Metrics:**
- Accuracy, F1-Score, Cohen's Kappa, AUC
- Per-class metrics
- Training time
- Parameter counts

### 2. Data Efficiency Experiment

**Data Percentages:** 10%, 25%, 50%, 75%, 100%

**Models Tested:**
- DCA
- ResNet-18, ResNet-50
- EfficientNet-B0
- STN-Affine

**Output:**
- `data_efficiency_results.json` - Full results
- `data_efficiency_curve.png` - Learning curve (Figure 3)
- `data_efficiency_summary.csv` - Summary table

### 3. Ablation Study

**Variants Tested:**
1. Full DCA (all components)
2. Without diffeomorphic constraint
3. Without conformal energy loss
4. Without both (STN only)
5. No transformation (ResNet-18 baseline)

**Output:**
- `ablation_results.json` - Full results
- `ablation_comparison.png` - Bar chart (Table 2)
- `ablation_summary.csv` - Summary table

### 4. Hyperparameter Sensitivity

**Parameters Tested:**
1. Conformal energy weight (λ): [0.0, 0.01, 0.05, 0.1, 0.5, 1.0]
2. Grid resolution: [4, 8, 16, 24, 32]
3. Number of diffeomorphic layers: [1, 2, 3, 4]

**Output:**
- `hyperparameter_results.json` - Full results
- `hyperparameter_sensitivity.png` - Sensitivity curves (Figure 4)
- `{param}_summary.csv` - Summary for each parameter

### 5. Robustness Analysis

**Perturbations Tested:**
1. Gaussian noise: std = [0.0, 0.05, 0.1, 0.15, 0.2]
2. Gaussian blur: kernel = [0, 3, 5, 7, 9]
3. Brightness: factor = [0.5, 0.75, 1.0, 1.25, 1.5]
4. Rotation: angle = [0°, 15°, 30°, 45°, 60°]

**Models Tested:**
- DCA
- ResNet-18
- STN-Affine

**Output:**
- `robustness_results.json` - Full results
- `robustness_comparison.png` - Robustness curves (Figure 5)

## Configuration

All experiments use the configuration file `configs/default.yaml`. You can override settings via command line:

```bash
# Override data directory
python run_all_experiments.py --data_dir /path/to/data

# Override in individual experiment
python -m src.experiments.comparison --data_dir /path/to/data
```

## Expected Runtime

With NVIDIA A100 GPU:
- Main Comparison: ~4-6 hours
- Data Efficiency: ~3-4 hours
- Ablation Study: ~2-3 hours
- Hyperparameter: ~2-3 hours
- Robustness: ~1-2 hours

**Total: ~12-18 hours for all experiments**

## Output Structure

```
logs/
├── main_comparison/
│   ├── comparison_results.json
│   ├── summary_table.csv
│   └── {model}_best.pth
├── data_efficiency/
│   ├── data_efficiency_results.json
│   ├── data_efficiency_curve.png
│   └── data_efficiency_summary.csv
├── ablation_study/
│   ├── ablation_results.json
│   ├── ablation_comparison.png
│   └── ablation_summary.csv
├── hyperparameter_sensitivity/
│   ├── hyperparameter_results.json
│   ├── hyperparameter_sensitivity.png
│   └── {param}_summary.csv
└── robustness/
    ├── robustness_results.json
    └── robustness_comparison.png
```

## Reproducing Paper Results

To reproduce the exact results from the paper:

1. Ensure you have the correct dataset split
2. Set the random seed in `configs/default.yaml` (seed: 42)
3. Run all experiments:
   ```bash
   python run_all_experiments.py
   ```
4. Results will be saved in the `logs/` directory

## Troubleshooting

**Out of Memory:**
- Reduce batch size in config: `batch_size: 16`
- Reduce number of workers: `num_workers: 2`

**Missing checkpoints:**
- Robustness experiment requires trained models from comparison experiment
- Run comparison experiment first

**CUDA not available:**
- Code will automatically fallback to CPU
- Expect much longer runtimes

## Citation

If you use this code, please cite:

```bibtex
@article{yourpaper2024,
  title={Deep Conformal Alignment for Histopathology Image Classification},
  author={Your Name},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  year={2024}
}
```
