"""Visualization and analysis utilities."""

from .confusion_matrix import plot_confusion_matrix, compute_confusion_matrix
from .learning_curves import plot_learning_curves, plot_data_efficiency
from .deformation_viz import visualize_deformation_fields, visualize_semantic_adaptation
from .per_class_analysis import analyze_per_class_performance, plot_per_class_results
from .result_aggregator import aggregate_results, generate_latex_tables

__all__ = [
    'plot_confusion_matrix',
    'compute_confusion_matrix',
    'plot_learning_curves',
    'plot_data_efficiency',
    'visualize_deformation_fields',
    'visualize_semantic_adaptation',
    'analyze_per_class_performance',
    'plot_per_class_results',
    'aggregate_results',
    'generate_latex_tables',
]
