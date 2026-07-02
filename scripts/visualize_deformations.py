"""Visualize learned deformation fields from trained DCA model."""

import argparse
import torch
from pathlib import Path
from torch.utils.data import DataLoader
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.models import create_model
from src.dataset import HistopathologyDataset, get_transforms
from src.visualization import visualize_deformation_fields, visualize_semantic_adaptation
from src.config import load_config


def visualize_deformations(checkpoint_path: str, data_dir: str, output_dir: str, num_samples: int = 5):
    """
    Visualize learned deformation fields from a trained model.
    
    Args:
        checkpoint_path: Path to model checkpoint
        data_dir: Dataset directory
        output_dir: Output directory for visualizations
        num_samples: Number of samples to visualize per class
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    config = checkpoint.get('config', None)
    
    if config is None:
        print("Loading default config")
        config = load_config('configs/default.yaml')
    
    print(f"Loading model from {checkpoint_path}")
    model = create_model(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    dataset = HistopathologyDataset(
        root_dir=data_dir,
        split='test',
        transform=get_transforms(split='test')
    )
    
    loader = DataLoader(dataset, batch_size=num_samples, shuffle=True, num_workers=0)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating visualizations...")
    
    with torch.no_grad():
        batch = next(iter(loader))
        images = batch['image'].to(device)
        labels = batch['label'].to(device)
        
        if hasattr(model, 'localization_net'):
            velocity_field = model.localization_net(images)
            deformation_field = model.scaling_squaring(velocity_field)
            transformed_images = model.warp(images, deformation_field)
        else:
            print("Model does not have spatial transformer components")
            return
        
        visualize_deformation_fields(
            images=images[:num_samples],
            deformation_fields=deformation_field[:num_samples],
            transformed_images=transformed_images[:num_samples],
            class_names=dataset.classes,
            save_path=str(output_dir / 'deformation_fields.pdf'),
            num_samples=num_samples
        )
    
    print("Generating semantic adaptation visualization...")
    
    images_by_class = {}
    deformations_by_class = {}
    
    for cls_idx in range(len(dataset.classes)):
        class_samples = [(img, lbl) for img, lbl in dataset if lbl == cls_idx]
        
        if len(class_samples) == 0:
            continue
        
        sample_img, _ = class_samples[0]
        sample_img = sample_img.unsqueeze(0).to(device)
        
        with torch.no_grad():
            if hasattr(model, 'localization_net'):
                velocity_field = model.localization_net(sample_img)
                deformation_field = model.scaling_squaring(velocity_field)
                
                images_by_class[cls_idx] = [sample_img[0]]
                deformations_by_class[cls_idx] = [deformation_field[0]]
    
    if images_by_class:
        visualize_semantic_adaptation(
            images_by_class=images_by_class,
            deformations_by_class=deformations_by_class,
            class_names=dataset.classes,
            save_path=str(output_dir / 'semantic_adaptation.pdf')
        )
    
    print(f"Visualizations saved to {output_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize learned deformations')
    parser.add_argument('--checkpoint', type=str, required=True, help='Model checkpoint path')
    parser.add_argument('--data_dir', type=str, required=True, help='Dataset directory')
    parser.add_argument('--output_dir', type=str, default='visualizations', help='Output directory')
    parser.add_argument('--num_samples', type=int, default=5, help='Number of samples to visualize')
    
    args = parser.parse_args()
    
    visualize_deformations(args.checkpoint, args.data_dir, args.output_dir, args.num_samples)
