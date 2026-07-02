"""
Spatial Transformer Network (STN) baselines with Affine and TPS transformations.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class STNAffine(nn.Module):
    """Spatial Transformer Network with Affine transformation."""
    
    def __init__(self, num_classes: int = 9, backbone: str = 'resnet18'):
        super(STNAffine, self).__init__()
        
        # Localization network
        self.localization = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
        )
        
        # Regressor for affine parameters
        self.fc_loc = nn.Sequential(
            nn.Linear(128 * 28 * 28, 256),
            nn.ReLU(True),
            nn.Linear(256, 6)  # 2x3 affine matrix
        )
        
        # Initialize to identity transformation
        self.fc_loc[2].weight.data.zero_()
        self.fc_loc[2].bias.data.copy_(torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float))
        
        # Feature extractor
        if backbone == 'resnet18':
            self.feature_extractor = models.resnet18(pretrained=True)
            num_ftrs = self.feature_extractor.fc.in_features
            self.feature_extractor.fc = nn.Linear(num_ftrs, num_classes)
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
    
    def stn(self, x):
        """Spatial transformer network."""
        xs = self.localization(x)
        xs = xs.view(xs.size(0), -1)
        theta = self.fc_loc(xs)
        theta = theta.view(-1, 2, 3)
        
        grid = F.affine_grid(theta, x.size(), align_corners=True)
        x_transformed = F.grid_sample(x, grid, align_corners=True)
        
        return x_transformed, theta
    
    def forward(self, x):
        x_transformed, theta = self.stn(x)
        output = self.feature_extractor(x_transformed)
        return output


class TPSGrid(nn.Module):
    """Thin Plate Spline grid generation."""
    
    def __init__(self, target_height: int, target_width: int, target_control_points: torch.Tensor):
        super(TPSGrid, self).__init__()
        self.target_height = target_height
        self.target_width = target_width
        self.register_buffer('target_control_points', target_control_points)
        
        N = target_control_points.size(0)
        
        # Create P matrix (Eq. 3 in Bookstein 1989)
        forward_kernel = self.compute_partial_repr(target_control_points, target_control_points)
        forward_kernel = torch.cat([torch.ones(N, 1), target_control_points, forward_kernel], dim=1)
        
        # Create L matrix
        zeros = torch.zeros(3, 3)
        P = torch.cat([target_control_points.T, torch.ones(1, N)], dim=0)
        L = torch.cat([torch.cat([forward_kernel, P.T], dim=1),
                       torch.cat([P, zeros], dim=1)], dim=0)
        
        self.register_buffer('L_inv', torch.inverse(L))
    
    @staticmethod
    def compute_partial_repr(input_points, control_points):
        """Compute radial basis function."""
        N = input_points.size(0)
        M = control_points.size(0)
        
        pairwise_diff = input_points.view(N, 1, 2) - control_points.view(1, M, 2)
        pairwise_diff_square = pairwise_diff * pairwise_diff
        
        pairwise_dist = pairwise_diff_square[:, :, 0] + pairwise_diff_square[:, :, 1]
        
        repr_matrix = 0.5 * pairwise_dist * torch.log(pairwise_dist + 1e-6)
        
        return repr_matrix
    
    def forward(self, source_control_points):
        """
        Generate TPS grid.
        
        Args:
            source_control_points: (B, N, 2) source control point coordinates
            
        Returns:
            Sampling grid (B, H, W, 2)
        """
        B = source_control_points.size(0)
        N = self.target_control_points.size(0)
        
        # Compute mapping parameters
        Y = torch.cat([source_control_points, torch.zeros(B, 3, 2, device=source_control_points.device)], dim=1)
        mapping_params = torch.matmul(self.L_inv, Y)
        
        # Create target grid
        HW = self.target_height * self.target_width
        y, x = torch.meshgrid(
            torch.linspace(-1, 1, self.target_height, device=source_control_points.device),
            torch.linspace(-1, 1, self.target_width, device=source_control_points.device)
        )
        grid = torch.stack([x.flatten(), y.flatten()], dim=1).unsqueeze(0).expand(B, -1, -1)
        
        # Compute TPS transformation
        partial_repr = self.compute_partial_repr(grid, self.target_control_points.unsqueeze(0).expand(B, -1, -1).reshape(B * N, 2)).reshape(B, HW, N)
        
        grid_padded = torch.cat([torch.ones(B, HW, 1, device=grid.device), grid, partial_repr], dim=2)
        
        grid_transformed = torch.matmul(grid_padded, mapping_params)
        
        grid_transformed = grid_transformed.view(B, self.target_height, self.target_width, 2)
        
        return grid_transformed


class STNTPS(nn.Module):
    """Spatial Transformer Network with Thin Plate Spline transformation."""
    
    def __init__(self, num_classes: int = 9, backbone: str = 'resnet18', num_control_points: int = 16):
        super(STNTPS, self).__init__()
        
        # Create control point grid (4x4 for 16 points)
        grid_size = int(num_control_points ** 0.5)
        x = torch.linspace(-0.9, 0.9, grid_size)
        y = torch.linspace(-0.9, 0.9, grid_size)
        xx, yy = torch.meshgrid(x, y)
        target_control_points = torch.stack([xx.flatten(), yy.flatten()], dim=1)
        
        # Localization network
        self.localization = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        # Regressor for control point offsets
        self.fc_loc = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(True),
            nn.Linear(256, num_control_points * 2)  # x,y offsets for each control point
        )
        
        # Initialize to zero offset (identity transformation)
        self.fc_loc[2].weight.data.zero_()
        self.fc_loc[2].bias.data.zero_()
        
        # TPS grid generator
        self.tps = TPSGrid(224, 224, target_control_points)
        
        # Feature extractor
        if backbone == 'resnet18':
            self.feature_extractor = models.resnet18(pretrained=True)
            num_ftrs = self.feature_extractor.fc.in_features
            self.feature_extractor.fc = nn.Linear(num_ftrs, num_classes)
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
    
    def stn(self, x):
        """Spatial transformer network with TPS."""
        xs = self.localization(x)
        xs = xs.view(xs.size(0), -1)
        
        # Predict control point offsets
        offsets = self.fc_loc(xs)
        offsets = offsets.view(xs.size(0), -1, 2)
        
        # Add offsets to target control points
        source_control_points = self.tps.target_control_points.unsqueeze(0) + offsets * 0.1  # Small offsets
        
        # Generate TPS grid
        grid = self.tps(source_control_points)
        
        # Apply transformation
        x_transformed = F.grid_sample(x, grid, align_corners=True)
        
        return x_transformed, source_control_points
    
    def forward(self, x):
        x_transformed, control_points = self.stn(x)
        output = self.feature_extractor(x_transformed)
        return output
