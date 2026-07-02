import os
import glob
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split

class HistopathologyDataset(Dataset):
    def __init__(self, root_dir, split='train', val_size=0.2, test_size=0.1, seed=42, transform=None, data_fraction=1.0):
        """
        Args:
            root_dir (str): Path to the dataset root directory containing class subfolders.
            split (str): One of 'train', 'val', 'test'.
            val_size (float): Proportion of dataset to include in the validation split.
            test_size (float): Proportion of dataset to include in the test split.
            seed (int): Random seed for reproducibility.
            transform (callable, optional): Optional transform to be applied on a sample.
            data_fraction (float): Fraction of data to use (0.0 < data_fraction <= 1.0).
        """
        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        
        all_image_paths = []
        all_labels = []
        
        for cls_name in self.classes:
            cls_dir = os.path.join(root_dir, cls_name)
            # Support common image extensions
            for ext in ['*.tif', '*.png', '*.jpg', '*.jpeg']:
                images = glob.glob(os.path.join(cls_dir, ext))
                all_image_paths.extend(images)
                all_labels.extend([self.class_to_idx[cls_name]] * len(images))
        
        # Split dataset
        # First split into train+val and test
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            all_image_paths, all_labels, test_size=test_size, random_state=seed, stratify=all_labels
        )
        
        # Then split train+val into train and val
        # Adjust val_size to be relative to the original dataset size if possible, 
        # but standard sklearn split is relative to the input. 
        # Here val_size is fraction of total, so we need to adjust for the remaining train_val set.
        # relative_val_size = val_size / (1 - test_size)
        
        relative_val_size = val_size / (1 - test_size)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=relative_val_size, random_state=seed, stratify=y_train_val
        )
        
        if split == 'train':
            self.image_paths = X_train
            self.labels = y_train
            
            # Subsample if needed
            if data_fraction < 1.0:
                n_samples = int(len(self.image_paths) * data_fraction)
                # Stratified subsampling
                X_sub, _, y_sub, _ = train_test_split(
                    self.image_paths, self.labels, train_size=n_samples, random_state=seed, stratify=self.labels
                )
                self.image_paths = X_sub
                self.labels = y_sub
                
        elif split == 'val':
            self.image_paths = X_val
            self.labels = y_val
        elif split == 'test':
            self.image_paths = X_test
            self.labels = y_test
        else:
            raise ValueError(f"Invalid split: {split}. Must be one of 'train', 'val', 'test'.")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a dummy image or handle error appropriately
            # For now, let's just re-raise or return None (which might break collate_fn)
            raise e
            
        if self.transform:
            image = self.transform(image)
            
        return image, label

def get_transforms(img_size=224, split='train'):
    if split == 'train':
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(15),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
