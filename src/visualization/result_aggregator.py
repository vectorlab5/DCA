"""Result aggregation and LaTeX table generation."""

import numpy as np
import json
from typing import Dict, List
from pathlib import Path


def aggregate_results(results_dict: Dict, output_file: str = None) -> Dict:
    """
    Aggregate results across multiple folds/runs.
    
    Args:
        results_dict: Nested dict with results
        output_file: Optional JSON file to save results
        
    Returns:
        Aggregated results with mean and std
    """
    aggregated = {}
    
    for method_name, method_results in results_dict.items():
        if isinstance(method_results, dict):
            if 'accuracy' in method_results:
                if isinstance(method_results['accuracy'], list):
                    aggregated[method_name] = {
                        'accuracy_mean': np.mean(method_results['accuracy']),
                        'accuracy_std': np.std(method_results['accuracy']),
                        'f1_mean': np.mean(method_results.get('f1', [])),
                        'f1_std': np.std(method_results.get('f1', [])),
                        'kappa_mean': np.mean(method_results.get('kappa', [])),
                        'kappa_std': np.std(method_results.get('kappa', []))
                    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(aggregated, f, indent=2)
    
    return aggregated


def generate_latex_tables(results_dict: Dict, 
                          table_type: str = 'main_results',
                          output_file: str = None) -> str:
    """
    Generate LaTeX tables from results.
    
    Args:
        results_dict: Dictionary with results
        table_type: Type of table ('main_results', 'ablation', 'data_efficiency', etc.)
        output_file: Optional file to save LaTeX code
        
    Returns:
        LaTeX table string
    """
    if table_type == 'main_results':
        latex = generate_main_results_table(results_dict)
    elif table_type == 'ablation':
        latex = generate_ablation_table(results_dict)
    elif table_type == 'data_efficiency':
        latex = generate_data_efficiency_table(results_dict)
    elif table_type == 'per_class':
        latex = generate_per_class_table(results_dict)
    elif table_type == 'hyperparameter':
        latex = generate_hyperparameter_table(results_dict)
    else:
        latex = "% Unknown table type\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(latex)
    
    return latex


def generate_main_results_table(results: Dict) -> str:
    """Generate LaTeX for main results table."""
    latex = r"""
\begin{table}[t]
\centering
\caption{Classification Performance on NCT-CRC-HE-100K (5-fold CV)}
\label{tab:main_results}
\setlength{\tabcolsep}{3pt}
\begin{tabular}{lccc}
\hline
\textbf{Method} & \textbf{Acc. (\%)} & \textbf{F1 (\%)} & \textbf{Kappa} \\
\hline
"""
    
    categories = {
        'Standard CNNs': ['ResNet-18', 'ResNet-50', 'DenseNet-121', 'EfficientNet-B0'],
        'Spatial Transformer Methods': ['STN-Affine', 'STN-TPS', 'Deformable Conv'],
        'Geometric Normalization': ['CEM', 'SEM'],
        'Stain Normalization': ['Macenko', 'StainGAN'],
        'Self-Supervised & Foundation Models': ['SimCLR', 'PLIP (linear)', 'PLIP (fine-tuned)', 
                                                'UNI (linear)', 'UNI (fine-tuned)', 'CONCH (linear)', 'CONCH (fine-tuned)']
    }
    
    for category, methods in categories.items():
        latex += f"\\multicolumn{{4}}{{l}}{{\\textit{{{category}}}}} \\\\\n"
        for method in methods:
            if method in results:
                r = results[method]
                acc_mean = r.get('accuracy_mean', 0)
                acc_std = r.get('accuracy_std', 0)
                f1_mean = r.get('f1_mean', 0)
                f1_std = r.get('f1_std', 0)
                kappa_mean = r.get('kappa_mean', 0)
                
                latex += f"{method} & {acc_mean:.1f}$\\pm${acc_std:.1f} & {f1_mean:.1f}$\\pm${f1_std:.1f} & {kappa_mean:.3f} \\\\\n"
        latex += "\\hline\n"
    
    if 'DCA' in results:
        r = results['DCA']
        latex += f"\\textbf{{DCA (Ours)}} & \\textbf{{{r['accuracy_mean']:.1f}$\\pm${r['accuracy_std']:.1f}}} & \\textbf{{{r['f1_mean']:.1f}$\\pm${r['f1_std']:.1f}}} & \\textbf{{{r['kappa_mean']:.3f}}} \\\\\n"
    
    latex += r"""
\hline
\end{tabular}
\end{table}
"""
    
    return latex


def generate_ablation_table(results: Dict) -> str:
    """Generate LaTeX for ablation study table."""
    latex = r"""
\begin{table}[t]
\centering
\caption{Ablation Study on DCA Components}
\label{tab:ablation}
\begin{tabular}{lccc}
\hline
\textbf{Configuration} & \textbf{Acc. (\%)} & \textbf{F1 (\%)} & \textbf{$\Delta$Acc.} \\
\hline
"""
    
    if 'Full DCA' in results:
        r = results['Full DCA']
        full_acc = r['accuracy_mean']
        latex += f"Full DCA & \\textbf{{{full_acc:.1f}$\\pm${r['accuracy_std']:.1f}}} & \\textbf{{{r['f1_mean']:.1f}$\\pm${r['f1_std']:.1f}}} & -- \\\\\n"
        latex += "\\hline\n"
        
        for config_name, config_results in results.items():
            if config_name != 'Full DCA':
                acc_mean = config_results['accuracy_mean']
                delta = acc_mean - full_acc
                latex += f"{config_name} & {acc_mean:.1f}$\\pm${config_results['accuracy_std']:.1f} & {config_results['f1_mean']:.1f}$\\pm${config_results['f1_std']:.1f} & {delta:+.1f} \\\\\n"
    
    latex += r"""
\hline
\end{tabular}
\end{table}
"""
    
    return latex


def generate_data_efficiency_table(results: Dict) -> str:
    """Generate LaTeX for data efficiency table."""
    latex = r"""
\begin{table}[t]
\centering
\caption{Test Accuracy (\%) vs. Training Data Fraction}
\label{tab:data_efficiency}
\begin{tabular}{lccccc}
\hline
\textbf{Method} & \textbf{5\%} & \textbf{10\%} & \textbf{20\%} & \textbf{50\%} & \textbf{100\%} \\
\hline
"""
    
    fractions = [0.05, 0.10, 0.20, 0.50, 1.00]
    
    for method_name, method_results in results.items():
        latex += f"{method_name}"
        for frac in fractions:
            if frac in method_results:
                mean, std = method_results[frac]
                latex += f" & {mean:.1f}$\\pm${std:.1f}"
            else:
                latex += " & --"
        latex += " \\\\\n"
    
    latex += r"""
\hline
\end{tabular}
\end{table}
"""
    
    return latex


def generate_per_class_table(results: Dict) -> str:
    """Generate LaTeX for per-class results table."""
    latex = r"""
\begin{table}[t]
\centering
\caption{Per-Class Test Accuracy (\%)}
\label{tab:per_class}
\begin{tabular}{lcccc}
\hline
\textbf{Class} & \textbf{ResNet-18} & \textbf{STN-TPS} & \textbf{DCA} & \textbf{$\Delta$} \\
\hline
"""
    
    for class_name, class_results in results.items():
        if isinstance(class_results, dict):
            resnet_acc = class_results.get('ResNet-18', 0)
            stn_acc = class_results.get('STN-TPS', 0)
            dca_acc = class_results.get('DCA', 0)
            delta = dca_acc - resnet_acc
            
            latex += f"{class_name} & {resnet_acc:.1f} & {stn_acc:.1f} & \\textbf{{{dca_acc:.1f}}} & {delta:+.1f} \\\\\n"
    
    latex += r"""
\hline
\end{tabular}
\end{table}
"""
    
    return latex


def generate_hyperparameter_table(results: Dict) -> str:
    """Generate LaTeX for hyperparameter sensitivity table."""
    latex = r"""
\begin{table}[t]
\centering
\caption{Hyperparameter Grid Search: Test Accuracy (\%)}
\label{tab:hyperparameter}
\begin{tabular}{l|ccccc}
\hline
$\lambda_{conf}$ \textbackslash{} $\lambda_{smooth}$ & 0.01 & 0.05 & 0.1 & 0.2 & 0.5 \\
\hline
"""
    
    lambda_conf_values = sorted(results.keys())
    lambda_smooth_values = sorted(results[lambda_conf_values[0]].keys())
    
    for lambda_conf in lambda_conf_values:
        latex += f"{lambda_conf}"
        for lambda_smooth in lambda_smooth_values:
            acc = results[lambda_conf].get(lambda_smooth, 0)
            if isinstance(acc, (list, tuple)):
                acc = acc[0]
            latex += f" & {acc:.1f}"
        latex += " \\\\\n"
    
    latex += r"""
\hline
\end{tabular}
\end{table}
"""
    
    return latex


def save_results_summary(results_dict: Dict, output_dir: str):
    """
    Save comprehensive results summary.
    
    Args:
        results_dict: All results
        output_dir: Directory to save summaries
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with open(output_dir / 'results_summary.json', 'w') as f:
        json.dump(results_dict, f, indent=2, default=lambda o: float(o) if isinstance(o, np.floating) else o)
    
    with open(output_dir / 'results_summary.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("EXPERIMENT RESULTS SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        for exp_name, exp_results in results_dict.items():
            f.write(f"\n{exp_name}:\n")
            f.write("-"*40 + "\n")
            
            if isinstance(exp_results, dict):
                for key, value in exp_results.items():
                    if isinstance(value, (float, np.floating)):
                        f.write(f"  {key}: {value:.4f}\n")
                    elif isinstance(value, (list, tuple)):
                        f.write(f"  {key}: {value}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
