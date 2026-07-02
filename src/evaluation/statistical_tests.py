"""
Statistical testing utilities for comparing models.
"""
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple
import pandas as pd


def paired_ttest(results_a: List[float], results_b: List[float], alternative: str = 'two-sided') -> Tuple[float, float]:
    """
    Perform paired t-test between two sets of results.
    
    Args:
        results_a: Results from model A (e.g., accuracy across folds)
        results_b: Results from model B
        alternative: 'two-sided', 'less', or 'greater'
        
    Returns:
        Tuple of (t-statistic, p-value)
    """
    results_a = np.array(results_a)
    results_b = np.array(results_b)
    
    t_stat, p_value = stats.ttest_rel(results_a, results_b, alternative=alternative)
    
    return t_stat, p_value


def wilcoxon_test(results_a: List[float], results_b: List[float], alternative: str = 'two-sided') -> Tuple[float, float]:
    """
    Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).
    
    Args:
        results_a: Results from model A
        results_b: Results from model B
        alternative: 'two-sided', 'less', or 'greater'
        
    Returns:
        Tuple of (statistic, p-value)
    """
    results_a = np.array(results_a)
    results_b = np.array(results_b)
    
    stat, p_value = stats.wilcoxon(results_a, results_b, alternative=alternative)
    
    return stat, p_value


def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Apply Bonferroni correction for multiple comparisons.
    
    Args:
        p_values: List of p-values
        alpha: Significance level
        
    Returns:
        List of booleans indicating significance after correction
    """
    n_tests = len(p_values)
    adjusted_alpha = alpha / n_tests
    
    return [p < adjusted_alpha for p in p_values]


def holm_bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Apply Holm-Bonferroni step-down correction (less conservative than Bonferroni).
    
    Args:
        p_values: List of p-values
        alpha: Significance level
        
    Returns:
        List of booleans indicating significance after correction
    """
    n_tests = len(p_values)
    
    # Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = np.array(p_values)[sorted_indices]
    
    # Compute adjusted alpha thresholds
    rejected = np.zeros(n_tests, dtype=bool)
    
    for i, (idx, p) in enumerate(zip(sorted_indices, sorted_p_values)):
        adjusted_alpha = alpha / (n_tests - i)
        if p < adjusted_alpha:
            rejected[idx] = True
        else:
            break  # Stop at first non-significant result
    
    return rejected.tolist()


def compute_effect_size(results_a: List[float], results_b: List[float]) -> float:
    """
    Compute Cohen's d effect size.
    
    Args:
        results_a: Results from model A
        results_b: Results from model B
        
    Returns:
        Effect size (Cohen's d)
    """
    results_a = np.array(results_a)
    results_b = np.array(results_b)
    
    diff = results_a - results_b
    pooled_std = np.sqrt((np.var(results_a) + np.var(results_b)) / 2)
    
    if pooled_std == 0:
        return 0.0
    
    return np.mean(diff) / pooled_std


def compare_multiple_models(
    results_dict: Dict[str, List[float]],
    reference_model: str,
    alpha: float = 0.05,
    correction_method: str = 'bonferroni'
) -> pd.DataFrame:
    """
    Compare multiple models against a reference model with multiple testing correction.
    
    Args:
        results_dict: Dictionary mapping model names to lists of results (e.g., CV accuracies)
        reference_model: Name of the reference model
        alpha: Significance level
        correction_method: 'bonferroni' or 'holm'
        
    Returns:
        DataFrame with comparison results
    """
    if reference_model not in results_dict:
        raise ValueError(f"Reference model '{reference_model}' not found in results")
    
    reference_results = results_dict[reference_model]
    other_models = [m for m in results_dict.keys() if m != reference_model]
    
    # Compute statistics for each comparison
    comparisons = []
    p_values = []
    
    for model in other_models:
        model_results = results_dict[model]
        
        # Compute mean and std
        mean_ref = np.mean(reference_results)
        mean_model = np.mean(model_results)
        std_ref = np.std(reference_results)
        std_model = np.std(model_results)
        
        # Compute difference
        diff = mean_model - mean_ref
        
        # Perform paired t-test
        t_stat, p_value = paired_ttest(model_results, reference_results)
        p_values.append(p_value)
        
        # Compute effect size
        effect_size = compute_effect_size(model_results, reference_results)
        
        comparisons.append({
            'model': model,
            'mean': mean_model,
            'std': std_model,
            'diff_vs_reference': diff,
            't_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size
        })
    
    # Apply multiple testing correction
    if correction_method == 'bonferroni':
        significant = bonferroni_correction(p_values, alpha)
    elif correction_method == 'holm':
        significant = holm_bonferroni_correction(p_values, alpha)
    else:
        raise ValueError(f"Unknown correction method: {correction_method}")
    
    for i, comp in enumerate(comparisons):
        comp['significant'] = significant[i]
    
    # Create DataFrame
    df = pd.DataFrame(comparisons)
    
    # Add reference model info at the top
    ref_row = {
        'model': f'{reference_model} (reference)',
        'mean': np.mean(reference_results),
        'std': np.std(reference_results),
        'diff_vs_reference': 0.0,
        't_statistic': np.nan,
        'p_value': np.nan,
        'effect_size': np.nan,
        'significant': False
    }
    df = pd.concat([pd.DataFrame([ref_row]), df], ignore_index=True)
    
    return df


def mcnemar_test(predictions_a: np.ndarray, predictions_b: np.ndarray, labels: np.ndarray) -> Tuple[float, float]:
    """
    Perform McNemar's test for comparing two classifiers.
    
    Args:
        predictions_a: Predictions from model A (N,)
        predictions_b: Predictions from model B (N,)
        labels: Ground truth labels (N,)
        
    Returns:
        Tuple of (statistic, p-value)
    """
    # Create contingency table
    # n01: A correct, B incorrect
    # n10: A incorrect, B correct
    correct_a = (predictions_a == labels)
    correct_b = (predictions_b == labels)
    
    n01 = np.sum(correct_a & ~correct_b)
    n10 = np.sum(~correct_a & correct_b)
    
    # Compute McNemar statistic with continuity correction
    statistic = ((np.abs(n01 - n10) - 1) ** 2) / (n01 + n10) if (n01 + n10) > 0 else 0
    
    # Chi-square test with 1 degree of freedom
    p_value = 1 - stats.chi2.cdf(statistic, df=1)
    
    return statistic, p_value


def format_significance(p_value: float) -> str:
    """
    Format p-value as significance marker.
    
    Args:
        p_value: P-value
        
    Returns:
        Significance marker string
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'
