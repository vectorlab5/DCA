"""Per-class performance analysis."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import torch


def analyze_per_class_performance(predictions_by_class: Dict[int, np.ndarray],
                                  targets_by_class: Dict[int, np.ndarray],
                                  class_names: List[str]) -> Dict:
    """
    Analyze per-class performance metrics.
    
    Args:
        predictions_by_class: Dict mapping class idx to predictions
        targets_by_class: Dict mapping class idx to targets
        class_names: List of class names
        
    Returns:
        Dictionary with per-class metrics
    """
    results = {}
    
    for cls_idx in range(len(class_names)):
        if cls_idx not in predictions_by_class:
            continue
        
        preds = predictions_by_class[cls_idx]
        targets = targets_by_class[cls_idx]
        
        if torch.is_tensor(preds):
            if preds.dim() > 1:
                preds = torch.argmax(preds, dim=1)
            preds = preds.cpu().numpy()
        
        if torch.is_tensor(targets):
            targets = targets.cpu().numpy()
        
        acc = accuracy_score(targets, preds) * 100
        f1 = f1_score(targets, preds, average='micro', zero_division=0) * 100
        precision = precision_score(targets, preds, average='micro', zero_division=0) * 100
        recall = recall_score(targets, preds, average='micro', zero_division=0) * 100
        
        results[class_names[cls_idx]] = {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'num_samples': len(targets)
        }
    
    return results


def compute_morphological_variability(features_by_class: Dict[int, np.ndarray]) -> Dict[int, float]:
    """
    Compute morphological variability as mean pairwise distance.
    
    Args:
        features_by_class: Dict mapping class idx to feature arrays (N, D)
        
    Returns:
        Dict mapping class idx to morphological variability score
    """
    mv_scores = {}
    
    for cls_idx, features in features_by_class.items():
        if torch.is_tensor(features):
            features = features.cpu().numpy()
        
        N = features.shape[0]
        if N < 2:
            mv_scores[cls_idx] = 0.0
            continue
        
        dists = []
        for i in range(N):
            for j in range(i+1, N):
                dist = np.linalg.norm(features[i] - features[j])
                dists.append(dist)
        
        mv_scores[cls_idx] = np.mean(dists) if dists else 0.0
    
    return mv_scores


def plot_per_class_results(baseline_results: Dict[str, Dict],
                           method_results: Dict[str, Dict],
                           baseline_name: str = 'ResNet-18',
                           method_name: str = 'DCA',
                           save_path: str = None):
    """
    Plot per-class accuracy comparison.
    
    Args:
        baseline_results: Per-class results for baseline
        method_results: Per-class results for method
        baseline_name: Name of baseline
        method_name: Name of method
        save_path: Path to save figure
    """
    class_names = list(baseline_results.keys())
    
    baseline_accs = [baseline_results[c]['accuracy'] for c in class_names]
    method_accs = [method_results[c]['accuracy'] for c in class_names]
    improvements = [method_accs[i] - baseline_accs[i] for i in range(len(class_names))]
    
    x = np.arange(len(class_names))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    bars1 = ax1.bar(x - width/2, baseline_accs, width, label=baseline_name, 
                    color='steelblue', alpha=0.8)
    bars2 = ax1.bar(x + width/2, method_accs, width, label=method_name, 
                    color='coral', alpha=0.8)
    
    ax1.set_ylabel('Accuracy (%)', fontsize=13)
    ax1.set_title('Per-Class Accuracy Comparison', fontsize=14, pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(class_names, fontsize=11)
    ax1.legend(fontsize=12)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.set_ylim(0, 105)
    
    for i, (b1, b2) in enumerate(zip(bars1, bars2)):
        height1 = b1.get_height()
        height2 = b2.get_height()
        ax1.text(b1.get_x() + b1.get_width()/2., height1 + 1,
                f'{height1:.1f}', ha='center', va='bottom', fontsize=9)
        ax1.text(b2.get_x() + b2.get_width()/2., height2 + 1,
                f'{height2:.1f}', ha='center', va='bottom', fontsize=9)
    
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    bars3 = ax2.bar(x, improvements, width*2, color=colors, alpha=0.7)
    
    ax2.set_ylabel('Improvement (%)', fontsize=13)
    ax2.set_title(f'{method_name} Improvement over {baseline_name}', fontsize=13)
    ax2.set_xticks(x)
    ax2.set_xticklabels(class_names, fontsize=11)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.grid(True, axis='y', alpha=0.3)
    
    for i, (bar, imp) in enumerate(zip(bars3, improvements)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -0.5),
                f'{imp:+.1f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def plot_accuracy_vs_variability(per_class_improvements: Dict[str, float],
                                 morphological_variability: Dict[str, float],
                                 save_path: str = None):
    """
    Plot correlation between accuracy improvement and morphological variability.
    
    Args:
        per_class_improvements: Dict mapping class name to accuracy improvement
        morphological_variability: Dict mapping class name to MV score
        save_path: Path to save figure
    """
    class_names = list(per_class_improvements.keys())
    improvements = [per_class_improvements[c] for c in class_names]
    mv_scores = [morphological_variability[c] for c in class_names]
    
    plt.figure(figsize=(10, 7))
    
    plt.scatter(mv_scores, improvements, s=150, alpha=0.7, color='steelblue', edgecolors='black')
    
    for i, name in enumerate(class_names):
        plt.annotate(name, (mv_scores[i], improvements[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=11)
    
    z = np.polyfit(mv_scores, improvements, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(mv_scores), max(mv_scores), 100)
    plt.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Linear fit')
    
    from scipy.stats import pearsonr
    corr, p_value = pearsonr(mv_scores, improvements)
    
    plt.xlabel('Morphological Variability (MV)', fontsize=13)
    plt.ylabel('Accuracy Improvement (%)', fontsize=13)
    plt.title(f'Accuracy Improvement vs. Morphological Variability\nPearson r = {corr:.3f}, p = {p_value:.4f}', 
             fontsize=13, pad=15)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()
