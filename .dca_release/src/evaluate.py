"""Comprehensive evaluation script for trained models."""

import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

from src.models import create_model
from src.dataset import HistopathologyDataset, get_transforms
from src.evaluation import MetricsCalculator, compute_bootstrap_ci
from src.visualization import (
    plot_confusion_matrix,
    compute_confusion_matrix,
    analyze_per_class_performance
)
from src.config import load_config


def evaluate_model(checkpoint_path: str, 
                   data_dir: str, 
                   output_dir: str,
                   split: str = 'test',
                   batch_size: int = 32):
    """
    Comprehensive evaluation of a trained model.
    
    Args:
        checkpoint_path: Path to model checkpoint
        data_dir: Dataset directory
        output_dir: Output directory for results
        split: Data split to evaluate on
        batch_size: Batch size for evaluation
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
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
        split=split,
        transform=get_transforms(split='test')
    )
    
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Evaluating on {len(dataset)} {split} samples...")
    
    all_predictions = []
    all_targets = []
    all_logits = []
    
    metrics_calc = MetricsCalculator(num_classes=len(dataset.classes))
    
    with torch.no_grad():
        for batch in tqdm(loader, desc="Evaluating"):
            images = batch['image'].to(device)
            labels = batch['label'].to(device)
            
            if hasattr(model, 'forward'):
                outputs = model(images)
                
                if isinstance(outputs, dict):
                    logits = outputs['logits']
                elif isinstance(outputs, tuple):
                    logits = outputs[0]
                else:
                    logits = outputs
            
            predictions = torch.argmax(logits, dim=1)
            
            all_predictions.extend(predictions.cpu().numpy())
            all_targets.extend(labels.cpu().numpy())
            all_logits.extend(logits.cpu().numpy())
            
            metrics_calc.update(predictions, labels)
    
    all_predictions = np.array(all_predictions)
    all_targets = np.array(all_targets)
    all_logits = np.array(all_logits)
    
    results = metrics_calc.compute()
    
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    print(f"Overall Accuracy: {results['accuracy']:.2f}%")
    print(f"Macro F1 Score: {results['macro_f1']:.2f}%")
    print(f"Cohen's Kappa: {results['kappa']:.4f}")
    print(f"Balanced Accuracy: {results['balanced_accuracy']:.2f}%")
    print("="*80)
    
    print("\nComputing confidence intervals...")
    ci_results = compute_bootstrap_ci(all_targets, all_predictions, n_bootstrap=1000)
    print(f"Accuracy 95% CI: [{ci_results['accuracy_ci'][0]:.2f}, {ci_results['accuracy_ci'][1]:.2f}]")
    print(f"Macro F1 95% CI: [{ci_results['macro_f1_ci'][0]:.2f}, {ci_results['macro_f1_ci'][1]:.2f}]")
    
    print("\nPer-class results:")
    print("-"*80)
    print(f"{'Class':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support'}")
    print("-"*80)
    
    for idx, class_name in enumerate(dataset.classes):
        precision = results['per_class_precision'][idx]
        recall = results['per_class_recall'][idx]
        f1 = results['per_class_f1'][idx]
        support = results['per_class_support'][idx]
        print(f"{class_name:<15} {precision:<12.2f} {recall:<12.2f} {f1:<12.2f} {support}")
    
    print("-"*80)
    
    cm = compute_confusion_matrix(all_predictions, all_targets, len(dataset.classes))
    
    plot_confusion_matrix(
        cm,
        class_names=dataset.classes,
        save_path=str(output_dir / 'confusion_matrix.pdf'),
        normalize=True,
        title=f'Confusion Matrix ({split.capitalize()} Set)'
    )
    print(f"\nConfusion matrix saved to {output_dir / 'confusion_matrix.pdf'}")
    
    results_dict = {
        'overall': {
            'accuracy': float(results['accuracy']),
            'macro_f1': float(results['macro_f1']),
            'kappa': float(results['kappa']),
            'balanced_accuracy': float(results['balanced_accuracy']),
            'accuracy_ci': [float(x) for x in ci_results['accuracy_ci']],
            'macro_f1_ci': [float(x) for x in ci_results['macro_f1_ci']]
        },
        'per_class': {}
    }
    
    for idx, class_name in enumerate(dataset.classes):
        results_dict['per_class'][class_name] = {
            'precision': float(results['per_class_precision'][idx]),
            'recall': float(results['per_class_recall'][idx]),
            'f1': float(results['per_class_f1'][idx]),
            'support': int(results['per_class_support'][idx])
        }
    
    with open(output_dir / 'evaluation_results.json', 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"Results saved to {output_dir / 'evaluation_results.json'}")
    
    np.savez(
        output_dir / 'predictions.npz',
        predictions=all_predictions,
        targets=all_targets,
        logits=all_logits
    )
    print(f"Predictions saved to {output_dir / 'predictions.npz'}")
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    
    return results_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate trained model')
    parser.add_argument('--checkpoint', type=str, required=True, help='Model checkpoint path')
    parser.add_argument('--data_dir', type=str, required=True, help='Dataset directory')
    parser.add_argument('--output_dir', type=str, default='evaluation_results', help='Output directory')
    parser.add_argument('--split', type=str, default='test', choices=['train', 'val', 'test'], 
                       help='Data split to evaluate')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    
    args = parser.parse_args()
    
    evaluate_model(
        checkpoint_path=args.checkpoint,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        split=args.split,
        batch_size=args.batch_size
    )
