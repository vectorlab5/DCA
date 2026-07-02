"""
SimCLR (Simple Framework for Contrastive Learning of Visual Representations) implementation.

Paper: https://arxiv.org/abs/2002.05709
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class ProjectionHead(nn.Module):
    """Projection head for SimCLR."""
    
    def __init__(self, input_dim: int = 512, hidden_dim: int = 2048, output_dim: int = 128):
        super(ProjectionHead, self).__init__()
        self.projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.projection(x)


class SimCLRModel(nn.Module):
    """SimCLR model for self-supervised pretraining."""
    
    def __init__(self, backbone: str = 'resnet18', projection_dim: int = 128):
        super(SimCLRModel, self).__init__()
        
        # Encoder
        if backbone == 'resnet18':
            self.encoder = models.resnet18(pretrained=False)
            feature_dim = self.encoder.fc.in_features
            self.encoder.fc = nn.Identity()  # Remove classification head
        elif backbone == 'resnet50':
            self.encoder = models.resnet50(pretrained=False)
            feature_dim = self.encoder.fc.in_features
            self.encoder.fc = nn.Identity()
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Projection head
        self.projection_head = ProjectionHead(
            input_dim=feature_dim,
            hidden_dim=2048,
            output_dim=projection_dim
        )
        
        self.feature_dim = feature_dim
    
    def forward(self, x):
        """Forward pass for SimCLR."""
        features = self.encoder(x)
        projections = self.projection_head(features)
        return features, projections


class NTXentLoss(nn.Module):
    """Normalized Temperature-scaled Cross Entropy Loss (NT-Xent) for SimCLR."""
    
    def __init__(self, temperature: float = 0.5):
        super(NTXentLoss, self).__init__()
        self.temperature = temperature
    
    def forward(self, z_i, z_j):
        """
        Compute NT-Xent loss.
        
        Args:
            z_i: Projections from augmentation 1 (B, D)
            z_j: Projections from augmentation 2 (B, D)
            
        Returns:
            Loss value
        """
        batch_size = z_i.size(0)
        
        # Normalize projections
        z_i = F.normalize(z_i, dim=1)
        z_j = F.normalize(z_j, dim=1)
        
        # Concatenate projections
        z = torch.cat([z_i, z_j], dim=0)  # (2B, D)
        
        # Compute similarity matrix
        sim_matrix = torch.matmul(z, z.T) / self.temperature  # (2B, 2B)
        
        # Create positive pair mask
        mask = torch.eye(2 * batch_size, dtype=torch.bool, device=z.device)
        
        # Create labels for positive pairs
        # For each sample i in batch, positive pair is at i+B (or i-B)
        labels = torch.cat([torch.arange(batch_size, 2 * batch_size),
                           torch.arange(batch_size)], dim=0).to(z.device)
        
        # Remove diagonal (self-similarity)
        sim_matrix = sim_matrix.masked_fill(mask, float('-inf'))
        
        # Compute loss
        loss = F.cross_entropy(sim_matrix, labels)
        
        return loss


class SimCLRFineTuneModel(nn.Module):
    """SimCLR model for supervised fine-tuning after pretraining."""
    
    def __init__(self, encoder: nn.Module, num_classes: int = 9, feature_dim: int = 512):
        super(SimCLRFineTuneModel, self).__init__()
        self.encoder = encoder
        self.classifier = nn.Linear(feature_dim, num_classes)
    
    def forward(self, x):
        """Forward pass for fine-tuning."""
        features = self.encoder(x)
        logits = self.classifier(features)
        return logits
    
    @classmethod
    def from_pretrained_simclr(cls, simclr_model: SimCLRModel, num_classes: int = 9):
        """
        Create fine-tune model from pretrained SimCLR.
        
        Args:
            simclr_model: Pretrained SimCLR model
            num_classes: Number of classes for supervised task
            
        Returns:
            SimCLRFineTuneModel instance
        """
        return cls(
            encoder=simclr_model.encoder,
            num_classes=num_classes,
            feature_dim=simclr_model.feature_dim
        )


def get_simclr_transforms():
    """
    Get data augmentation transforms for SimCLR.
    
    Returns:
        Tuple of (transform1, transform2) for creating positive pairs
    """
    from torchvision import transforms
    
    # SimCLR augmentation pipeline
    color_jitter = transforms.ColorJitter(0.8, 0.8, 0.8, 0.2)
    
    transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.2, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomApply([color_jitter], p=0.8),
        transforms.RandomGrayscale(p=0.2),
        transforms.GaussianBlur(kernel_size=23, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return transform, transform


def pretrain_simclr(
    model: SimCLRModel,
    train_loader: torch.utils.data.DataLoader,
    num_epochs: int = 200,
    learning_rate: float = 0.0003,
    temperature: float = 0.5,
    device: str = 'cuda'
):
    """
    Pretrain SimCLR model.
    
    Args:
        model: SimCLR model
        train_loader: DataLoader with paired augmentations
        num_epochs: Number of pretraining epochs
        learning_rate: Learning rate
        temperature: Temperature for NT-Xent loss
        device: Device to train on
        
    Returns:
        Pretrained model
    """
    model = model.to(device)
    criterion = NTXentLoss(temperature=temperature)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        for (x_i, x_j), _ in train_loader:
            x_i = x_i.to(device)
            x_j = x_j.to(device)
            
            # Forward pass
            _, z_i = model(x_i)
            _, z_j = model(x_j)
            
            # Compute loss
            loss = criterion(z_i, z_j)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")
    
    return model
