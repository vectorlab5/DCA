"""Evaluation module for metrics, logging, and cross-validation."""

from .metrics import (
    MetricsCalculator,
    compute_metrics_from_logits,
    aggregate_cv_results,
    format_metrics_table
)
from .logger import Logger, MetricsLogger, CheckpointManager
from .statistical_tests import (
    paired_ttest,
    wilcoxon_test,
    bonferroni_correction,
    holm_bonferroni_correction,
    compute_effect_size,
    compare_multiple_models,
    mcnemar_test,
    format_significance
)
from .cross_validation import CrossValidator, stratified_split_dataset

__all__ = [
    'MetricsCalculator',
    'compute_metrics_from_logits',
    'aggregate_cv_results',
    'format_metrics_table',
    'Logger',
    'MetricsLogger',
    'CheckpointManager',
    'paired_ttest',
    'wilcoxon_test',
    'bonferroni_correction',
    'holm_bonferroni_correction',
    'compute_effect_size',
    'compare_multiple_models',
    'mcnemar_test',
    'format_significance',
    'CrossValidator',
    'stratified_split_dataset'
]
