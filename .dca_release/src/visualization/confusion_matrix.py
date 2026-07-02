"""Confusion matrix computation and visualization."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import torch


def compute_confusion_matrix(predictions, targets, num_classes):
    """
    Compute confusion matrix from predictions and targets.
    
    Args:
        predictions: Model predictions (logits or class indices)
        targets: Ground truth labels
        num_classes: Number of classes
        
    Returns:
        Confusion matrix as numpy array
    """
    if torch.is_tensor(predictions):
        if predictions.dim() > 1:
            predictions = torch.argmax(predictions, dim=1)
        predictions = predictions.cpu().numpy()
    
    if torch.is_tensor(targets):
        targets = targets.cpu().numpy()
    
    cm = confusion_matrix(targets, predictions, labels=np.arange(num_classes))
    return cm


def plot_confusion_matrix(cm, class_names, save_path=None, normalize=True, title=None):
    """
    Plot confusion matrix with nice formatting.
    
    Args:
        cm: Confusion matrix array
        class_names: List of class names
        save_path: Path to save figure
        normalize: Whether to normalize by row
        title: Optional title
    """
    if normalize:
        cm = cm.astype('float') / (cm.sum(axis=1)[:, np.newaxis] + 1e-10) * 100
        fmt = '.1f'
        cbar_label = 'Percentage (%)'
    else:
        fmt = 'd'
        cbar_label = 'Count'
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': cbar_label}, vmin=0, vmax=100 if normalize else None)
    
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    
    if title:
        plt.title(title, fontsize=14, pad=15)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def plot_confusion_comparison(cm1, cm2, class_names, method1_name='Method 1', 
                              method2_name='Method 2', save_path=None):
    """
    Plot side-by-side confusion matrices for comparison.
    
    Args:
        cm1: First confusion matrix
        cm2: Second confusion matrix
        class_names: List of class names
        method1_name: Name of first method
        method2_name: Name of second method
        save_path: Path to save figure
    """
    cm1_norm = cm1.astype('float') / (cm1.sum(axis=1)[:, np.newaxis] + 1e-10) * 100
    cm2_norm = cm2.astype('float') / (cm2.sum(axis=1)[:, np.newaxis] + 1e-10) * 100
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    for idx, (cm, title, ax) in enumerate([(cm1_norm, method1_name, axes[0]), 
                                             (cm2_norm, method2_name, axes[1])]):
        sns.heatmap(cm, annot=True, fmt='.1f', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Percentage (%)'}, vmin=0, vmax=100,
                   ax=ax)
        ax.set_ylabel('True Label', fontsize=11)
        ax.set_xlabel('Predicted Label', fontsize=11)
        ax.set_title(title, fontsize=13, pad=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def analyze_confusion_improvements(cm_baseline, cm_method, class_names, threshold=5.0):
    """
    Analyze improvements in confusion patterns.
    
    Args:
        cm_baseline: Baseline confusion matrix
        cm_method: Method confusion matrix
        class_names: List of class names
        threshold: Minimum improvement percentage to report
        
    Returns:
        Dictionary with improvements
    """
    cm_baseline_norm = cm_baseline.astype('float') / (cm_baseline.sum(axis=1)[:, np.newaxis] + 1e-10) * 100
    cm_method_norm = cm_method.astype('float') / (cm_method.sum(axis=1)[:, np.newaxis] + 1e-10) * 100
    
    improvements = []
    
    num_classes = len(class_names)
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j:
                baseline_conf = cm_baseline_norm[i, j]
                method_conf = cm_method_norm[i, j]
                improvement = baseline_conf - method_conf
                
                if improvement >= threshold:
                    improvements.append({
                        'true_class': class_names[i],
                        'pred_class': class_names[j],
                        'baseline_conf': baseline_conf,
                        'method_conf': method_conf,
                        'improvement': improvement
                    })
    
    improvements.sort(key=lambda x: x['improvement'], reverse=True)
    
    return improvements
