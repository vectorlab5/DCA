"""Verify dataset structure and integrity."""

import argparse
from pathlib import Path
from collections import defaultdict


def verify_dataset(data_dir: str):
    """
    Verify dataset structure and print statistics.
    
    Args:
        data_dir: Dataset directory to verify
    """
    data_dir = Path(data_dir)
    
    if not data_dir.exists():
        print(f"ERROR: Directory {data_dir} does not exist")
        return False
    
    splits = ['train', 'val', 'test']
    
    print("="*80)
    print("DATASET VERIFICATION")
    print("="*80)
    print(f"Data directory: {data_dir}\n")
    
    all_classes = set()
    split_stats = defaultdict(lambda: defaultdict(int))
    
    for split in splits:
        split_dir = data_dir / split
        if not split_dir.exists():
            print(f"WARNING: Split directory '{split}' not found")
            continue
        
        class_dirs = [d for d in split_dir.iterdir() if d.is_dir()]
        
        for class_dir in class_dirs:
            class_name = class_dir.name
            all_classes.add(class_name)
            
            images = list(class_dir.glob('*.tif')) + list(class_dir.glob('*.png')) + list(class_dir.glob('*.jpg'))
            split_stats[split][class_name] = len(images)
    
    all_classes = sorted(all_classes)
    
    print(f"Found {len(all_classes)} classes: {', '.join(all_classes)}\n")
    
    print("-"*80)
    print(f"{'Class':<15} {'Train':<12} {'Val':<12} {'Test':<12} {'Total':<12}")
    print("-"*80)
    
    totals = {'train': 0, 'val': 0, 'test': 0}
    
    for class_name in all_classes:
        train_count = split_stats['train'][class_name]
        val_count = split_stats['val'][class_name]
        test_count = split_stats['test'][class_name]
        total = train_count + val_count + test_count
        
        totals['train'] += train_count
        totals['val'] += val_count
        totals['test'] += test_count
        
        print(f"{class_name:<15} {train_count:<12} {val_count:<12} {test_count:<12} {total:<12}")
    
    print("-"*80)
    grand_total = sum(totals.values())
    print(f"{'TOTAL':<15} {totals['train']:<12} {totals['val']:<12} {totals['test']:<12} {grand_total:<12}")
    print("-"*80)
    
    print("\nSplit Proportions:")
    if grand_total > 0:
        for split in splits:
            proportion = totals[split] / grand_total * 100
            print(f"  {split.capitalize()}: {totals[split]} images ({proportion:.1f}%)")
    
    print("\nClass Balance (Train):")
    if totals['train'] > 0:
        for class_name in all_classes:
            count = split_stats['train'][class_name]
            proportion = count / totals['train'] * 100
            print(f"  {class_name}: {count} images ({proportion:.1f}%)")
    
    print("\n" + "="*80)
    
    issues = []
    
    if len(all_classes) == 0:
        issues.append("No classes found")
    
    for split in splits:
        if totals[split] == 0:
            issues.append(f"No images in {split} split")
    
    for class_name in all_classes:
        for split in splits:
            if split_stats[split][class_name] == 0:
                issues.append(f"No images for class '{class_name}' in {split} split")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("VERIFICATION PASSED: Dataset structure is correct")
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify dataset structure')
    parser.add_argument('--data_dir', type=str, required=True, help='Dataset directory to verify')
    
    args = parser.parse_args()
    
    success = verify_dataset(args.data_dir)
    exit(0 if success else 1)
