import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class DiffeomorphicSTN(nn.Module):
    def __init__(self, in_channels=3, grid_size=32):
        """
        Diffeomorphic Spatial Transformer Network.
        Predicts a velocity field 'v' and integrates it to get deformation field 'phi'.
        """
        super(DiffeomorphicSTN, self).__init__()
        self.grid_size = grid_size
        
        # Localization Network (UNet-like or simple CNN) to predict velocity field
        # Input: (B, C, H, W) -> Output: (B, 2, H, W)
        # We use a lightweight CNN for efficiency
        self.localization = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2), # 112
            
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2), # 56
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2), # 28
            
            nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True), # 56
            
            nn.Conv2d(64, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True), # 112
            
            nn.Conv2d(32, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True), # 224
            
            nn.Conv2d(16, 2, kernel_size=3, stride=1, padding=1) # Output velocity field (vx, vy)
        )
        
        # Initialize the last layer with small weights to start close to identity
        self.localization[-1].weight.data.fill_(0)
        self.localization[-1].bias.data.fill_(0)

    def integrate_velocity(self, v):
        """
        Integrates velocity field 'v' using scaling and squaring.
        v: (B, 2, H, W)
        """
        n_steps = 7 # 2^7 = 128 steps
        flow = v / (2 ** n_steps)
        
        for _ in range(n_steps):
            flow = flow + self.warp_flow(flow, flow)
            
        return flow

    def warp_flow(self, flow, displacement):
        """
        Warps a flow field by another displacement field.
        flow(x + displacement(x))
        """
        B, C, H, W = flow.shape
        # Create identity grid
        grid = self.get_grid(B, H, W, flow.device)
        
        # The sampling grid is identity + displacement
        # We need to normalize displacement to [-1, 1] range for grid_sample
        # But here 'displacement' is in pixel units or normalized units?
        # Let's assume flow is in normalized coordinates [-1, 1] for simplicity of implementation
        
        sample_grid = grid + displacement.permute(0, 2, 3, 1)
        
        warped_flow = F.grid_sample(flow, sample_grid, mode='bilinear', padding_mode='border', align_corners=True)
        return warped_flow

    def get_grid(self, B, H, W, device):
        y, x = torch.meshgrid(torch.linspace(-1, 1, H, device=device), torch.linspace(-1, 1, W, device=device))
        grid = torch.stack((x, y), dim=2) # (H, W, 2)
        grid = grid.unsqueeze(0).repeat(B, 1, 1, 1) # (B, H, W, 2)
        return grid

    def forward(self, x):
        B, C, H, W = x.shape
        
        # Predict velocity field
        v = self.localization(x) # (B, 2, H, W)
        
        # Integrate to get deformation field phi (displacement)
        # We assume v is in [-1, 1] coordinate space
        phi = self.integrate_velocity(v)
        
        # Warp input image
        grid = self.get_grid(B, H, W, x.device)
        sample_grid = grid + phi.permute(0, 2, 3, 1)
        
        warped_x = F.grid_sample(x, sample_grid, mode='bilinear', padding_mode='border', align_corners=True)
        
        return warped_x, phi, v

class FeatureExtractor(nn.Module):
    def __init__(self, num_classes=9, backbone='resnet18'):
        super(FeatureExtractor, self).__init__()
        if backbone == 'resnet18':
            self.model = models.resnet18(pretrained=True)
        elif backbone == 'resnet50':
            self.model = models.resnet50(pretrained=True)
        else:
            raise ValueError("Backbone not supported")
            
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.model(x)

class DCANet(nn.Module):
    def __init__(self, num_classes=9, backbone='resnet18'):
        super(DCANet, self).__init__()
        self.stn = DiffeomorphicSTN()
        self.feature_extractor = FeatureExtractor(num_classes=num_classes, backbone=backbone)

    def forward(self, x):
        warped_x, phi, v = self.stn(x)
        logits = self.feature_extractor(warped_x)
        return logits, warped_x, phi, v
