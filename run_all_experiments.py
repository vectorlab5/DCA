"""
Master script to run all experiments.
"""
import argparse
import os
import sys
from datetime import datetime

from src.experiments import (
    run_comparison_experiment,
    run_data_efficiency_experiment,
    run_ablation_experiment,
    run_hyperparameter_experiment,
    run_robustness_experiment
)


def run_all_experiments(config_path: str, data_dir: str = None):
    """
    Run all experiments sequentially.
    
    Args:
        config_path: Path to config file
        data_dir: Optional data directory override
    """
    start_time = datetime.now()
    
    print("="*80)
    print("RUNNING ALL EXPERIMENTS")
    print("="*80)
    print(f"Start time: {start_time}")
    print(f"Config: {config_path}")
    if data_dir:
        print(f"Data directory: {data_dir}")
    print("="*80 + "\n")
    
    overrides = {}
    if data_dir:
        overrides['data_dir'] = data_dir
    
    experiments_to_run = [
        ("Main Comparison", run_comparison_experiment),
        ("Data Efficiency", run_data_efficiency_experiment),
        ("Ablation Study", run_ablation_experiment),
        ("Hyperparameter Sensitivity", run_hyperparameter_experiment),
        ("Robustness Analysis", run_robustness_experiment),
    ]
    
    results = {}
    
    for exp_name, exp_fn in experiments_to_run:
        print(f"\n{'#'*80}")
        print(f"# {exp_name}")
        print(f"{'#'*80}\n")
        
        try:
            exp_results = exp_fn(config_path, **overrides)
            results[exp_name] = {
                'status': 'success',
                'results': exp_results
            }
            print(f"\n✓ {exp_name} completed successfully")
        except Exception as e:
            print(f"\n✗ {exp_name} failed: {str(e)}")
            import traceback
            traceback.print_exc()
            results[exp_name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "="*80)
    print("ALL EXPERIMENTS SUMMARY")
    print("="*80)
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print(f"Duration: {duration}")
    print("\nExperiment Status:")
    print("-"*80)
    
    for exp_name, result in results.items():
        status_symbol = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_symbol} {exp_name}: {result['status'].upper()}")
    
    print("="*80 + "\n")
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run DCA experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all experiments
  python run_all_experiments.py --config configs/default.yaml
  
  # Run specific experiment
  python run_all_experiments.py --experiment comparison --config configs/default.yaml
  
  # Override data directory
  python run_all_experiments.py --data_dir /path/to/data
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='configs/default.yaml',
        help='Path to config file'
    )
    
    parser.add_argument(
        '--data_dir',
        type=str,
        help='Override data directory'
    )
    
    parser.add_argument(
        '--experiment',
        type=str,
        choices=['all', 'comparison', 'data_efficiency', 'ablation', 
                'hyperparameter', 'robustness'],
        default='all',
        help='Which experiment to run'
    )
    
    args = parser.parse_args()
    
    # Check config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)
    
    # Build overrides
    overrides = {}
    if args.data_dir:
        overrides['data_dir'] = args.data_dir
    
    # Run experiments
    if args.experiment == 'all':
        run_all_experiments(args.config, args.data_dir)
    elif args.experiment == 'comparison':
        run_comparison_experiment(args.config, **overrides)
    elif args.experiment == 'data_efficiency':
        run_data_efficiency_experiment(args.config, **overrides)
    elif args.experiment == 'ablation':
        run_ablation_experiment(args.config, **overrides)
    elif args.experiment == 'hyperparameter':
        run_hyperparameter_experiment(args.config, **overrides)
    elif args.experiment == 'robustness':
        run_robustness_experiment(args.config, **overrides)


if __name__ == '__main__':
    main()
