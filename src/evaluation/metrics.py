"""
Comprehensive metrics computation for histopathology classification.
"""
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, f1_score, cohen_kappa_score,
    confusion_matrix, classification_report, roc_auc_score
)
from typing import Dict, List, Tuple, Optional
import pandas as pd


class MetricsCalculator:
    """Calculate and track various classification metrics."""
    
    def __init__(self, num_classes: int, class_names: Optional[List[str]] = None):
        """
        Initialize metrics calculator.
        
        Args:
            num_classes: Number of classes
            class_names: List of class names (optional)
        """
        self.num_classes = num_classes
        self.class_names = class_names or [f"Class_{i}" for i in range(num_classes)]
        self.reset()
    
    def reset(self):
        """Reset all accumulated predictions and labels."""
        self.all_preds = []
        self.all_labels = []
        self.all_probs = []
    
    def update(self, preds: torch.Tensor, labels: torch.Tensor, probs: Optional[torch.Tensor] = None):
        """
        Update metrics with new batch of predictions.
        
        Args:
            preds: Predicted class indices (B,)
            labels: Ground truth class indices (B,)
            probs: Class probabilities (B, num_classes) - optional
        """
        self.all_preds.extend(preds.cpu().numpy().tolist())
        self.all_labels.extend(labels.cpu().numpy().tolist())
        
        if probs is not None:
            self.all_probs.extend(probs.cpu().numpy().tolist())
    
    def compute(self) -> Dict[str, float]:
        """
        Compute all metrics.
        
        Returns:
            Dictionary containing all computed metrics
        """
        preds = np.array(self.all_preds)
        labels = np.array(self.all_labels)
        
        metrics = {}
        
        # Overall metrics
        metrics['accuracy'] = accuracy_score(labels, preds)
        metrics['f1_macro'] = f1_score(labels, preds, average='macro')
        metrics['f1_weighted'] = f1_score(labels, preds, average='weighted')
        metrics['kappa'] = cohen_kappa_score(labels, preds)
        
        # Per-class metrics
        per_class_f1 = f1_score(labels, preds, average=None)
        for i, class_name in enumerate(self.class_names):
            metrics[f'f1_{class_name}'] = per_class_f1[i]
        
        # Per-class accuracy
        cm = confusion_matrix(labels, preds)
        per_class_acc = cm.diagonal() / cm.sum(axis=1)
        for i, class_name in enumerate(self.class_names):
            metrics[f'accuracy_{class_name}'] = per_class_acc[i]
        
        # AUC if probabilities are available
        if len(self.all_probs) > 0:
            probs = np.array(self.all_probs)
            try:
                # One-vs-rest AUC for each class
                for i, class_name in enumerate(self.class_names):
                    binary_labels = (labels == i).astype(int)
                    class_probs = probs[:, i]
                    metrics[f'auc_{class_name}'] = roc_auc_score(binary_labels, class_probs)
                
                # Macro average AUC
                metrics['auc_macro'] = np.mean([metrics[f'auc_{cn}'] for cn in self.class_names])
            except:
                pass
        
        return metrics
    
    def get_confusion_matrix(self) -> np.ndarray:
        """
        Get confusion matrix.
        
        Returns:
            Confusion matrix (num_classes, num_classes)
        """
        return confusion_matrix(self.all_labels, self.all_preds)
    
    def get_classification_report(self) -> str:
        """
        Get detailed classification report.
        
        Returns:
            Classification report string
        """
        return classification_report(
            self.all_labels, 
            self.all_preds,
            target_names=self.class_names,
            digits=4
        )
    
    def compute_confidence_intervals(self, n_bootstrap: int = 1000, alpha: float = 0.05) -> Dict[str, Tuple[float, float]]:
        """
        Compute bootstrap confidence intervals for metrics.
        
        Args:
            n_bootstrap: Number of bootstrap samples
            alpha: Significance level (default 0.05 for 95% CI)
            
        Returns:
            Dictionary mapping metric names to (lower, upper) confidence bounds
        """
        preds = np.array(self.all_preds)
        labels = np.array(self.all_labels)
        n_samples = len(preds)
        
        # Bootstrap sampling
        acc_scores = []
        f1_scores = []
        
        np.random.seed(42)
        for _ in range(n_bootstrap):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            boot_preds = preds[indices]
            boot_labels = labels[indices]
            
            acc_scores.append(accuracy_score(boot_labels, boot_preds))
            f1_scores.append(f1_score(boot_labels, boot_preds, average='macro'))
        
        # Compute percentile-based confidence intervals
        lower_p = (alpha / 2) * 100
        upper_p = (1 - alpha / 2) * 100
        
        ci = {}
        ci['accuracy'] = (np.percentile(acc_scores, lower_p), np.percentile(acc_scores, upper_p))
        ci['f1_macro'] = (np.percentile(f1_scores, lower_p), np.percentile(f1_scores, upper_p))
        
        return ci


def compute_metrics_from_logits(
    logits: torch.Tensor,
    labels: torch.Tensor,
    num_classes: int,
    class_names: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Compute metrics directly from logits and labels.
    
    Args:
        logits: Model outputs (B, num_classes)
        labels: Ground truth labels (B,)
        num_classes: Number of classes
        class_names: List of class names (optional)
        
    Returns:
        Dictionary of metrics
    """
    probs = torch.softmax(logits, dim=1)
    preds = torch.argmax(logits, dim=1)
    
    calculator = MetricsCalculator(num_classes, class_names)
    calculator.update(preds, labels, probs)
    
    return calculator.compute()


def aggregate_cv_results(fold_results: List[Dict[str, float]]) -> Dict[str, Tuple[float, float]]:
    """
    Aggregate cross-validation results across folds.
    
    Args:
        fold_results: List of metric dictionaries, one per fold
        
    Returns:
        Dictionary mapping metric names to (mean, std) tuples
    """
    # Collect all metric names
    all_metrics = set()
    for result in fold_results:
        all_metrics.update(result.keys())
    
    aggregated = {}
    for metric in all_metrics:
        values = [result.get(metric, np.nan) for result in fold_results]
        values = [v for v in values if not np.isnan(v)]
        
        if len(values) > 0:
            aggregated[metric] = (np.mean(values), np.std(values))
    
    return aggregated


def format_metrics_table(metrics: Dict[str, float], decimals: int = 4) -> str:
    """
    Format metrics dictionary as a readable table.
    
    Args:
        metrics: Dictionary of metrics
        decimals: Number of decimal places
        
    Returns:
        Formatted string table
    """
    lines = ["Metrics:"]
    lines.append("-" * 50)
    
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            lines.append(f"{key:30s}: {value:.{decimals}f}")
        else:
            lines.append(f"{key:30s}: {value}")
    
    lines.append("-" * 50)
    return "\n".join(lines)
