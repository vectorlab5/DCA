"""
Logging utilities for training and evaluation.
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import torch


class Logger:
    """Enhanced logger with file and console output."""
    
    def __init__(self, log_dir: str, name: str = "dca", level: int = logging.INFO):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to save log files
            name: Logger name
            level: Logging level
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        self.log_file = log_file
    
    def info(self, msg: str):
        """Log info message."""
        self.logger.info(msg)
    
    def debug(self, msg: str):
        """Log debug message."""
        self.logger.debug(msg)
    
    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)
    
    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)
    
    def critical(self, msg: str):
        """Log critical message."""
        self.logger.critical(msg)


class MetricsLogger:
    """Logger for tracking metrics during training."""
    
    def __init__(self, log_dir: str, experiment_name: str):
        """
        Initialize metrics logger.
        
        Args:
            log_dir: Directory to save metrics
            experiment_name: Name of the experiment
        """
        self.log_dir = log_dir
        self.experiment_name = experiment_name
        os.makedirs(log_dir, exist_ok=True)
        
        self.train_metrics = []
        self.val_metrics = []
        self.test_metrics = {}
    
    def log_train_metrics(self, epoch: int, metrics: Dict[str, float]):
        """
        Log training metrics for an epoch.
        
        Args:
            epoch: Current epoch number
            metrics: Dictionary of metrics
        """
        entry = {'epoch': epoch, **metrics}
        self.train_metrics.append(entry)
    
    def log_val_metrics(self, epoch: int, metrics: Dict[str, float]):
        """
        Log validation metrics for an epoch.
        
        Args:
            epoch: Current epoch number
            metrics: Dictionary of metrics
        """
        entry = {'epoch': epoch, **metrics}
        self.val_metrics.append(entry)
    
    def log_test_metrics(self, metrics: Dict[str, float]):
        """
        Log final test metrics.
        
        Args:
            metrics: Dictionary of metrics
        """
        self.test_metrics = metrics
    
    def save(self):
        """Save all logged metrics to JSON files."""
        # Save training metrics
        if self.train_metrics:
            train_file = os.path.join(self.log_dir, f'{self.experiment_name}_train_metrics.json')
            with open(train_file, 'w') as f:
                json.dump(self.train_metrics, f, indent=2)
        
        # Save validation metrics
        if self.val_metrics:
            val_file = os.path.join(self.log_dir, f'{self.experiment_name}_val_metrics.json')
            with open(val_file, 'w') as f:
                json.dump(self.val_metrics, f, indent=2)
        
        # Save test metrics
        if self.test_metrics:
            test_file = os.path.join(self.log_dir, f'{self.experiment_name}_test_metrics.json')
            with open(test_file, 'w') as f:
                json.dump(self.test_metrics, f, indent=2)
    
    def get_best_epoch(self, metric: str = 'val_accuracy', mode: str = 'max') -> int:
        """
        Get the epoch with the best metric value.
        
        Args:
            metric: Metric name to optimize
            mode: 'max' or 'min'
            
        Returns:
            Best epoch number
        """
        if not self.val_metrics:
            return 0
        
        values = [m.get(metric, float('-inf') if mode == 'max' else float('inf')) 
                  for m in self.val_metrics]
        
        if mode == 'max':
            best_idx = max(range(len(values)), key=lambda i: values[i])
        else:
            best_idx = min(range(len(values)), key=lambda i: values[i])
        
        return self.val_metrics[best_idx]['epoch']


class CheckpointManager:
    """Manage model checkpoints during training."""
    
    def __init__(self, checkpoint_dir: str, max_checkpoints: int = 5):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to save checkpoints
            max_checkpoints: Maximum number of checkpoints to keep
        """
        self.checkpoint_dir = checkpoint_dir
        self.max_checkpoints = max_checkpoints
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        self.checkpoints = []
    
    def save_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        metrics: Dict[str, float],
        is_best: bool = False,
        extra_state: Optional[Dict[str, Any]] = None
    ):
        """
        Save a checkpoint.
        
        Args:
            model: Model to save
            optimizer: Optimizer to save
            epoch: Current epoch
            metrics: Metrics dictionary
            is_best: Whether this is the best checkpoint
            extra_state: Additional state to save
        """
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics
        }
        
        if extra_state:
            checkpoint.update(extra_state)
        
        # Save regular checkpoint
        checkpoint_path = os.path.join(self.checkpoint_dir, f'checkpoint_epoch_{epoch}.pth')
        torch.save(checkpoint, checkpoint_path)
        self.checkpoints.append((epoch, checkpoint_path))
        
        # Save best checkpoint
        if is_best:
            best_path = os.path.join(self.checkpoint_dir, 'best_model.pth')
            torch.save(checkpoint, best_path)
        
        # Remove old checkpoints
        if len(self.checkpoints) > self.max_checkpoints:
            _, old_path = self.checkpoints.pop(0)
            if os.path.exists(old_path):
                os.remove(old_path)
    
    def load_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        checkpoint_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load a checkpoint.
        
        Args:
            model: Model to load state into
            optimizer: Optimizer to load state into (optional)
            checkpoint_path: Path to checkpoint (if None, loads best_model.pth)
            
        Returns:
            Checkpoint dictionary
        """
        if checkpoint_path is None:
            checkpoint_path = os.path.join(self.checkpoint_dir, 'best_model.pth')
        
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        
        if optimizer is not None and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        return checkpoint
