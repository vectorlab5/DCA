"""
Cross-validation framework for robust model evaluation.
"""
import os
import numpy as np
import torch
from typing import Dict, List, Callable, Any, Optional
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import Dataset, Subset, DataLoader
import copy

from ..evaluation.metrics import MetricsCalculator, aggregate_cv_results
from ..evaluation.logger import Logger, MetricsLogger, CheckpointManager


class CrossValidator:
    """Framework for k-fold cross-validation."""
    
    def __init__(
        self,
        n_folds: int = 5,
        random_seeds: Optional[List[int]] = None,
        stratified: bool = True,
        shuffle: bool = True
    ):
        """
        Initialize cross-validator.
        
        Args:
            n_folds: Number of folds
            random_seeds: Random seeds for each fold (default: [42, 123, 456, 789, 1024])
            stratified: Use stratified splits
            shuffle: Shuffle data before splitting
        """
        self.n_folds = n_folds
        self.random_seeds = random_seeds or [42, 123, 456, 789, 1024]
        self.stratified = stratified
        self.shuffle = shuffle
        
        if len(self.random_seeds) != n_folds:
            raise ValueError(f"Number of random seeds ({len(self.random_seeds)}) must match n_folds ({n_folds})")
    
    def get_fold_splits(self, dataset: Dataset, labels: np.ndarray) -> List[tuple]:
        """
        Generate train/val/test indices for each fold.
        
        Args:
            dataset: Dataset to split
            labels: Labels for stratification
            
        Returns:
            List of (train_indices, val_indices, test_indices) tuples
        """
        n_samples = len(dataset)
        indices = np.arange(n_samples)
        
        if self.stratified:
            kfold = StratifiedKFold(
                n_splits=self.n_folds,
                shuffle=self.shuffle,
                random_state=self.random_seeds[0]
            )
        else:
            from sklearn.model_selection import KFold
            kfold = KFold(
                n_splits=self.n_folds,
                shuffle=self.shuffle,
                random_state=self.random_seeds[0]
            )
        
        fold_splits = []
        for train_val_idx, test_idx in kfold.split(indices, labels):
            # Further split train_val into train and val
            train_val_labels = labels[train_val_idx]
            
            if self.stratified:
                val_kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_seeds[0])
            else:
                val_kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_seeds[0])
            
            # Use first split for train/val
            for train_idx_rel, val_idx_rel in val_kfold.split(train_val_idx, train_val_labels):
                train_idx = train_val_idx[train_idx_rel]
                val_idx = train_val_idx[val_idx_rel]
                break
            
            fold_splits.append((train_idx, val_idx, test_idx))
        
        return fold_splits
    
    def run(
        self,
        dataset: Dataset,
        labels: np.ndarray,
        model_factory: Callable,
        train_fn: Callable,
        eval_fn: Callable,
        output_dir: str,
        experiment_name: str = "cv_experiment"
    ) -> Dict[str, Any]:
        """
        Run cross-validation.
        
        Args:
            dataset: Complete dataset
            labels: All labels for stratification
            model_factory: Function that returns a new model instance
            train_fn: Training function (model, train_loader, val_loader, config) -> trained_model
            eval_fn: Evaluation function (model, test_loader) -> metrics_dict
            output_dir: Directory to save results
            experiment_name: Name of experiment
            
        Returns:
            Dictionary with aggregated results
        """
        logger = Logger(output_dir, name=experiment_name)
        logger.info(f"Starting {self.n_folds}-fold cross-validation")
        
        fold_splits = self.get_fold_splits(dataset, labels)
        fold_results = []
        
        for fold, (train_idx, val_idx, test_idx) in enumerate(fold_splits):
            logger.info(f"\n{'='*60}")
            logger.info(f"Fold {fold + 1}/{self.n_folds}")
            logger.info(f"{'='*60}")
            logger.info(f"Train samples: {len(train_idx)}, Val samples: {len(val_idx)}, Test samples: {len(test_idx)}")
            
            # Set random seed for this fold
            torch.manual_seed(self.random_seeds[fold])
            np.random.seed(self.random_seeds[fold])
            
            # Create data subsets
            train_dataset = Subset(dataset, train_idx)
            val_dataset = Subset(dataset, val_idx)
            test_dataset = Subset(dataset, test_idx)
            
            # Create fresh model
            model = model_factory()
            
            # Train model
            fold_output_dir = os.path.join(output_dir, f"fold_{fold}")
            os.makedirs(fold_output_dir, exist_ok=True)
            
            trained_model = train_fn(
                model=model,
                train_dataset=train_dataset,
                val_dataset=val_dataset,
                output_dir=fold_output_dir,
                fold=fold
            )
            
            # Evaluate on test set
            test_metrics = eval_fn(trained_model, test_dataset)
            
            logger.info(f"\nFold {fold + 1} Test Results:")
            for metric, value in test_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
            
            fold_results.append(test_metrics)
        
        # Aggregate results
        aggregated = aggregate_cv_results(fold_results)
        
        logger.info(f"\n{'='*60}")
        logger.info("Cross-Validation Results (Mean ± Std)")
        logger.info(f"{'='*60}")
        
        for metric, (mean, std) in aggregated.items():
            logger.info(f"{metric:30s}: {mean:.4f} ± {std:.4f}")
        
        # Save results
        results = {
            'fold_results': fold_results,
            'aggregated_results': aggregated,
            'n_folds': self.n_folds,
            'random_seeds': self.random_seeds
        }
        
        import json
        results_file = os.path.join(output_dir, f'{experiment_name}_cv_results.json')
        with open(results_file, 'w') as f:
            # Convert to JSON-serializable format
            json_results = {
                'fold_results': fold_results,
                'aggregated_results': {k: {'mean': float(v[0]), 'std': float(v[1])} 
                                       for k, v in aggregated.items()},
                'n_folds': self.n_folds,
                'random_seeds': self.random_seeds
            }
            json.dump(json_results, f, indent=2)
        
        logger.info(f"\nResults saved to {results_file}")
        
        return results


def stratified_split_dataset(
    dataset: Dataset,
    labels: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    random_seed: int = 42
) -> tuple:
    """
    Split dataset into stratified train/val/test sets.
    
    Args:
        dataset: Dataset to split
        labels: Labels for stratification
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        random_seed: Random seed
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    from sklearn.model_selection import train_test_split
    
    if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
        raise ValueError("Ratios must sum to 1.0")
    
    n_samples = len(dataset)
    indices = np.arange(n_samples)
    
    # First split: train+val vs test
    train_val_idx, test_idx = train_test_split(
        indices,
        test_size=test_ratio,
        stratify=labels,
        random_state=random_seed
    )
    
    # Second split: train vs val
    relative_val_ratio = val_ratio / (train_ratio + val_ratio)
    train_idx, val_idx = train_test_split(
        train_val_idx,
        test_size=relative_val_ratio,
        stratify=labels[train_val_idx],
        random_state=random_seed
    )
    
    train_dataset = Subset(dataset, train_idx)
    val_dataset = Subset(dataset, val_idx)
    test_dataset = Subset(dataset, test_idx)
    
    return train_dataset, val_dataset, test_dataset
