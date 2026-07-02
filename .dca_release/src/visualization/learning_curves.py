"""Learning curve and data efficiency visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List


def plot_learning_curves(train_losses: List[float], val_losses: List[float],
                         train_accs: List[float], val_accs: List[float],
                         save_path: str = None):
    """
    Plot training and validation learning curves.
    
    Args:
        train_losses: Training loss per epoch
        val_losses: Validation loss per epoch
        train_accs: Training accuracy per epoch
        val_accs: Validation accuracy per epoch
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    epochs = range(1, len(train_losses) + 1)
    
    axes[0].plot(epochs, train_losses, 'b-', label='Train', linewidth=2)
    axes[0].plot(epochs, val_losses, 'r-', label='Validation', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=13)
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(epochs, train_accs, 'b-', label='Train', linewidth=2)
    axes[1].plot(epochs, val_accs, 'r-', label='Validation', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy (%)', fontsize=12)
    axes[1].set_title('Training and Validation Accuracy', fontsize=13)
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def plot_data_efficiency(results: Dict[str, Dict[float, tuple]], 
                        save_path: str = None,
                        show_ci: bool = True):
    """
    Plot data efficiency curves for multiple methods.
    
    Args:
        results: Dictionary mapping method names to {fraction: (mean, std)} tuples
        save_path: Path to save figure
        show_ci: Whether to show confidence intervals
    """
    plt.figure(figsize=(10, 6))
    
    colors = {
        'ResNet-18': '#1f77b4',
        'STN-TPS': '#ff7f0e',
        'CEM': '#2ca02c',
        'SimCLR + FT': '#d62728',
        'UNI (FT)': '#9467bd',
        'DCA': '#e377c2',
        'DCA + UNI': '#8c564b'
    }
    
    markers = {
        'ResNet-18': 'o',
        'STN-TPS': 's',
        'CEM': '^',
        'SimCLR + FT': 'v',
        'UNI (FT)': 'D',
        'DCA': '*',
        'DCA + UNI': 'P'
    }
    
    for method_name, method_results in results.items():
        fractions = sorted(method_results.keys())
        means = [method_results[f][0] for f in fractions]
        stds = [method_results[f][1] for f in fractions]
        
        color = colors.get(method_name, None)
        marker = markers.get(method_name, 'o')
        
        plt.plot([f*100 for f in fractions], means, marker=marker, 
                linewidth=2.5, markersize=8, label=method_name, color=color)
        
        if show_ci:
            ci_lower = [m - 1.96*s for m, s in zip(means, stds)]
            ci_upper = [m + 1.96*s for m, s in zip(means, stds)]
            plt.fill_between([f*100 for f in fractions], ci_lower, ci_upper, 
                           alpha=0.2, color=color)
    
    if 'DCA' in results and 0.1 in results['DCA']:
        dca_10_acc = results['DCA'][0.1][0]
        plt.axhline(y=dca_10_acc, color='red', linestyle='--', alpha=0.5, linewidth=1.5,
                   label=f'DCA @ 10% ({dca_10_acc:.1f}%)')
    
    plt.xlabel('Training Data Fraction (%)', fontsize=13)
    plt.ylabel('Test Accuracy (%)', fontsize=13)
    plt.title('Data Efficiency Comparison', fontsize=14, pad=15)
    plt.legend(fontsize=10, loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 105)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def compute_equivalent_data_ratio(baseline_results: Dict[float, tuple],
                                  method_results: Dict[float, tuple],
                                  target_fraction: float = 0.1) -> float:
    """
    Compute equivalent data ratio between method and baseline.
    
    Args:
        baseline_results: {fraction: (mean, std)} for baseline
        method_results: {fraction: (mean, std)} for method
        target_fraction: Fraction at which to compute equivalence
        
    Returns:
        Equivalent fraction for baseline
    """
    target_acc = method_results[target_fraction][0]
    
    fractions = sorted(baseline_results.keys())
    accs = [baseline_results[f][0] for f in fractions]
    
    for i in range(len(fractions) - 1):
        if accs[i] <= target_acc <= accs[i+1]:
            f1, f2 = fractions[i], fractions[i+1]
            a1, a2 = accs[i], accs[i+1]
            
            equiv_frac = f1 + (target_acc - a1) / (a2 - a1) * (f2 - f1)
            return equiv_frac
    
    return None


def plot_multiple_learning_curves(all_curves: Dict[str, Dict], save_path: str = None):
    """
    Plot learning curves for multiple methods on same plot.
    
    Args:
        all_curves: Dict mapping method names to {'train_loss', 'val_loss', 'train_acc', 'val_acc'}
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for method_name, curves in all_curves.items():
        epochs = range(1, len(curves['val_acc']) + 1)
        axes[0].plot(epochs, curves['val_loss'], linewidth=2, label=method_name, alpha=0.8)
        axes[1].plot(epochs, curves['val_acc'], linewidth=2, label=method_name, alpha=0.8)
    
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Validation Loss', fontsize=12)
    axes[0].set_title('Validation Loss Comparison', fontsize=13)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Validation Accuracy (%)', fontsize=12)
    axes[1].set_title('Validation Accuracy Comparison', fontsize=13)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()
