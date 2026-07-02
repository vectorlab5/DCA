# Deep Conformal Alignment for Histopathology Image Analysis

A PyTorch implementation for learning topology-preserving transformations in histopathology image classification.

## Overview

This framework applies conformal geometry principles to normalize morphological variability in histopathology images. The approach learns diffeomorphic transformations through velocity field parameterization with scaling-and-squaring integration, guided by a differentiable conformal energy loss.

**Key Features:**
- Learnable conformal geometry with differentiable energy regularization
- Improved data efficiency for limited annotation scenarios
- Compatible with pretrained foundation models
- Semantic adaptation to different tissue types

## Installation

**Requirements:**
- Python 3.8+
- PyTorch 2.0+
- CUDA 11.0+ (optional, for GPU)

```bash
# Clone and set up environment
git clone https://github.com/vectorlab5/DCA.git
cd DCA

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Dataset

This implementation uses the [NCT-CRC-HE-100K](https://zenodo.org/record/1214456) colorectal cancer histopathology dataset.

```bash
# Download and prepare
wget https://zenodo.org/record/1214456/files/NCT-CRC-HE-100K.zip
unzip NCT-CRC-HE-100K.zip -d data/

python scripts/prepare_dataset.py --data_dir data/NCT-CRC-HE-100K --output_dir data/processed
```

Expected structure:
```
data/processed/
├── train/
│   ├── ADI/
│   ├── BACK/
│   └── ...
├── val/
└── test/
```

## Usage

### Training

```bash
python src/train.py --config configs/default.yaml --data_dir data/processed
```

### Evaluation

```bash
python src/evaluate.py --checkpoint checkpoints/best.pth --data_dir data/processed
```

### Visualization

```bash
python scripts/visualize_deformations.py --checkpoint checkpoints/best.pth --output_dir visualizations/
```

## Configuration

Key parameters in `configs/default.yaml`:

```yaml
model:
  num_classes: 9
  lambda_conf: 1.0        # Conformal energy weight
  lambda_smooth: 0.1      # Smoothness regularization
  scaling_squaring_steps: 7

training:
  batch_size: 32
  epochs: 50
  learning_rate: 0.001
  optimizer: adamw
```

## Project Structure

```
├── configs/              # Configuration files
├── src/
│   ├── models/           # Model implementations
│   ├── evaluation/       # Metrics and evaluation
│   ├── visualization/    # Visualization tools
│   ├── dataset.py        # Data loading
│   ├── loss.py           # Loss functions
│   ├── train.py          # Training script
│   └── evaluate.py       # Evaluation script
├── scripts/              # Helper scripts
├── tests/                # Unit tests
└── requirements.txt
```

## Running Tests

```bash
pytest tests/
```

## Troubleshooting

**Out of Memory:** Reduce `batch_size` in config  
**CUDA Issues:** `pip install torch --index-url https://download.pytorch.org/whl/cu118`  
**Dataset Problems:** Run `python scripts/verify_dataset.py --data_dir data/processed`

## License

MIT License. See LICENSE for details.

## Acknowledgments

- NCT-CRC-HE-100K dataset
- VoxelMorph for diffeomorphic registration concepts
- Timm library for model implementations
