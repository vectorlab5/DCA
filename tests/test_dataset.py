import unittest
import os
import sys
import torch
from torch.utils.data import DataLoader

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dataset import HistopathologyDataset, get_transforms

class TestDataset(unittest.TestCase):
    def setUp(self):
        self.data_dir = '/Users/xiufengliu/Projects/paper_cancer/data'
        self.batch_size = 4

    def test_dataset_loading(self):
        # Test Train Split
        train_dataset = HistopathologyDataset(
            root_dir=self.data_dir, 
            split='train', 
            transform=get_transforms(split='train')
        )
        print(f"Train dataset size: {len(train_dataset)}")
        self.assertGreater(len(train_dataset), 0, "Train dataset should not be empty")
        
        # Test Val Split
        val_dataset = HistopathologyDataset(
            root_dir=self.data_dir, 
            split='val', 
            transform=get_transforms(split='val')
        )
        print(f"Val dataset size: {len(val_dataset)}")
        self.assertGreater(len(val_dataset), 0, "Val dataset should not be empty")

        # Test Test Split
        test_dataset = HistopathologyDataset(
            root_dir=self.data_dir, 
            split='test', 
            transform=get_transforms(split='test')
        )
        print(f"Test dataset size: {len(test_dataset)}")
        self.assertGreater(len(test_dataset), 0, "Test dataset should not be empty")
        
        # Check classes
        print(f"Classes: {train_dataset.classes}")
        self.assertTrue(len(train_dataset.classes) > 0)

    def test_dataloader(self):
        dataset = HistopathologyDataset(
            root_dir=self.data_dir, 
            split='train', 
            transform=get_transforms(split='train')
        )
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        images, labels = next(iter(loader))
        
        print(f"Batch shape: {images.shape}")
        print(f"Labels: {labels}")
        
        self.assertEqual(images.shape[0], self.batch_size)
        self.assertEqual(images.shape[1], 3) # RGB
        self.assertEqual(images.shape[2], 224) # Height
        self.assertEqual(images.shape[3], 224) # Width

if __name__ == '__main__':
    unittest.main()
