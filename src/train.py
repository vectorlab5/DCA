import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import argparse

from src.dataset import HistopathologyDataset, get_transforms
from src.model import DCANet
from src.loss import ConformalLoss, SmoothnessLoss
from src.utils import visualize_results, save_checkpoint

def train(args):
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Hyperparameters
    batch_size = args.batch_size
    learning_rate = args.lr
    num_epochs = args.epochs
    
    # Dataset
    train_dataset = HistopathologyDataset(
        root_dir=args.data_dir, 
        split='train', 
        transform=get_transforms(split='train'),
        data_fraction=args.data_fraction
    )
    val_dataset = HistopathologyDataset(
        root_dir=args.data_dir, 
        split='val', 
        transform=get_transforms(split='val')
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    
    # Model
    model = DCANet(num_classes=len(train_dataset.classes)).to(device)
    
    # Loss and Optimizer
    criterion_cls = nn.CrossEntropyLoss()
    criterion_conf = ConformalLoss(weight=args.conf_weight)
    criterion_smooth = SmoothnessLoss(weight=args.smooth_weight)
    
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training Loop
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        running_acc = 0.0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
        for i, (images, labels) in enumerate(pbar):
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            logits, warped_images, phi, v = model(images)
            
            # Compute losses
            loss_cls = criterion_cls(logits, labels)
            loss_conf = criterion_conf(phi)
            loss_smooth = criterion_smooth(phi) # Enforce smoothness on displacement
            
            loss = loss_cls + loss_conf + loss_smooth
            
            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, preds = torch.max(logits, 1)
            running_acc += torch.sum(preds == labels.data).item()
            
            pbar.set_postfix({'loss': loss.item(), 'cls': loss_cls.item(), 'conf': loss_conf.item()})
            
            if i == 0 and (epoch % args.vis_freq == 0):
                visualize_results(images, warped_images, phi, 
                                  os.path.join(args.save_dir, f"vis_epoch_{epoch}.png"), epoch)
        
        epoch_loss = running_loss / len(train_dataset)
        epoch_acc = running_acc / len(train_dataset)
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}")
        
        # Validation
        model.eval()
        val_acc = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                logits, _, _, _ = model(images)
                _, preds = torch.max(logits, 1)
                val_acc += torch.sum(preds == labels.data).item()
        
        val_acc /= len(val_dataset)
        print(f"Validation Acc: {val_acc:.4f}")
        
        if (epoch + 1) % args.save_freq == 0:
            save_checkpoint(model, optimizer, epoch+1, args.save_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='/Users/xiufengliu/Projects/paper_cancer/data')
    parser.add_argument('--save_dir', type=str, default='checkpoints')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--conf_weight', type=float, default=1.0)
    parser.add_argument('--smooth_weight', type=float, default=0.1)
    parser.add_argument('--vis_freq', type=int, default=1)
    parser.add_argument('--save_freq', type=int, default=5)
    parser.add_argument('--data_fraction', type=float, default=1.0, help='Fraction of training data to use')
    
    args = parser.parse_args()
    train(args)
