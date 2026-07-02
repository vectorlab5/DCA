"""Script to prepare and organize the dataset."""

import argparse
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm


def prepare_dataset(data_dir: str, output_dir: str, val_split: float = 0.2, test_split: float = 0.2, seed: int = 42):
    """
    Organize dataset into train/val/test splits.
    
    Args:
        data_dir: Source data directory
        output_dir: Output directory for organized dataset
        val_split: Validation set fraction
        test_split: Test set fraction
        seed: Random seed
    """
    np.random.seed(seed)
    
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(class_dirs)} classes")
    
    for split in ['train', 'val', 'test']:
        (output_dir / split).mkdir(parents=True, exist_ok=True)
    
    for class_dir in tqdm(class_dirs, desc="Processing classes"):
        class_name = class_dir.name
        
        for split in ['train', 'val', 'test']:
            (output_dir / split / class_name).mkdir(parents=True, exist_ok=True)
        
        all_images = list(class_dir.glob('*.tif')) + list(class_dir.glob('*.png')) + list(class_dir.glob('*.jpg'))
        
        train_val, test = train_test_split(all_images, test_size=test_split, random_state=seed)
        train, val = train_test_split(train_val, test_size=val_split/(1-test_split), random_state=seed)
        
        print(f"\n{class_name}: {len(all_images)} images -> Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        
        for img_path in tqdm(train, desc=f"  Copying {class_name} train", leave=False):
            shutil.copy(img_path, output_dir / 'train' / class_name / img_path.name)
        
        for img_path in tqdm(val, desc=f"  Copying {class_name} val", leave=False):
            shutil.copy(img_path, output_dir / 'val' / class_name / img_path.name)
        
        for img_path in tqdm(test, desc=f"  Copying {class_name} test", leave=False):
            shutil.copy(img_path, output_dir / 'test' / class_name / img_path.name)
    
    print(f"\nDataset prepared successfully in {output_dir}")
    
    for split in ['train', 'val', 'test']:
        n_images = sum(1 for _ in (output_dir / split).rglob('*.*') if _.is_file())
        print(f"  {split}: {n_images} images")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare dataset')
    parser.add_argument('--data_dir', type=str, required=True, help='Source data directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory')
    parser.add_argument('--val_split', type=float, default=0.2, help='Validation split fraction')
    parser.add_argument('--test_split', type=float, default=0.2, help='Test split fraction')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    prepare_dataset(args.data_dir, args.output_dir, args.val_split, args.test_split, args.seed)
