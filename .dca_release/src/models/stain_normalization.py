"""
Stain normalization wrappers for histopathology images.
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Optional
import warnings


class MacenkoNormalizer:
    """
    Macenko stain normalization.
    
    Paper: Macenko et al., "A method for normalizing histology slides for quantitative analysis", ISBI 2009
    """
    
    def __init__(self):
        # Reference stain matrix (H&E)
        self.target_stains = np.array([[0.5626, 0.2159],
                                       [0.7201, 0.8012],
                                       [0.4062, 0.5581]])
        self.target_concentrations = np.array([[1.9705, 1.0308]])
    
    def normalize(self, img: np.ndarray) -> np.ndarray:
        """
        Normalize staining of H&E image.
        
        Args:
            img: RGB image as numpy array (H, W, 3), values in [0, 255]
            
        Returns:
            Normalized image
        """
        # Reshape image
        h, w, c = img.shape
        img = img.reshape((-1, 3))
        
        # Calculate optical density
        OD = -np.log((img.astype(float) + 1) / 256)
        
        # Remove transparent pixels
        ODhat = OD[~np.any(OD < 0.15, axis=1)]
        
        if ODhat.shape[0] < 2:
            warnings.warn("Too few tissue pixels. Returning original image.")
            return img.reshape((h, w, c))
        
        # Compute eigenvectors
        try:
            eigvals, eigvecs = np.linalg.eigh(np.cov(ODhat.T))
        except:
            return img.reshape((h, w, c))
        
        # Project on plane spanned by first two eigenvectors
        That = ODhat.dot(eigvecs[:, 1:3])
        
        # Find min and max vectors
        phi = np.arctan2(That[:, 1], That[:, 0])
        minPhi = np.percentile(phi, 1)
        maxPhi = np.percentile(phi, 99)
        
        vMin = eigvecs[:, 1:3].dot(np.array([(np.cos(minPhi), np.sin(minPhi))]).T)
        vMax = eigvecs[:, 1:3].dot(np.array([(np.cos(maxPhi), np.sin(maxPhi))]).T)
        
        # Normalize stain matrix
        if vMin[0] > vMax[0]:
            HE = np.array((vMin[:, 0], vMax[:, 0])).T
        else:
            HE = np.array((vMax[:, 0], vMin[:, 0])).T
        
        # Rows of HE are H and E
        Y = np.reshape(OD, (-1, 3)).T
        
        C = np.linalg.lstsq(HE, Y, rcond=None)[0]
        
        # Normalize concentrations
        maxC = np.array([np.percentile(C[0, :], 99), np.percentile(C[1, :], 99)])
        
        if maxC[0] == 0 or maxC[1] == 0:
            return img.reshape((h, w, c))
        
        C2 = C * (self.target_concentrations / maxC[:, np.newaxis])
        
        # Recreate image using reference stain vectors
        Inorm = np.exp(-self.target_stains.dot(C2))
        Inorm = np.clip(Inorm, 0, 1)
        Inorm = np.reshape(Inorm.T, (h, w, 3))
        Inorm = (Inorm * 255).astype(np.uint8)
        
        return Inorm


class StainNormalizationWrapper(nn.Module):
    """Wrapper that applies stain normalization before model forward pass."""
    
    def __init__(self, base_model: nn.Module, normalizer: Optional[MacenkoNormalizer] = None):
        super(StainNormalizationWrapper, self).__init__()
        self.base_model = base_model
        self.normalizer = normalizer if normalizer is not None else MacenkoNormalizer()
    
    def normalize_batch(self, x: torch.Tensor) -> torch.Tensor:
        """
        Normalize a batch of images.
        
        Args:
            x: Batch of images (B, C, H, W) in range [0, 1] or normalized
            
        Returns:
            Normalized batch
        """
        # Denormalize if needed (assuming ImageNet normalization)
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(x.device)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(x.device)
        
        x_denorm = x * std + mean
        x_denorm = torch.clamp(x_denorm, 0, 1)
        
        # Convert to numpy for normalization
        x_np = (x_denorm * 255).cpu().numpy().astype(np.uint8)
        x_np = x_np.transpose(0, 2, 3, 1)  # (B, H, W, C)
        
        # Normalize each image in batch
        normalized_batch = []
        for i in range(x_np.shape[0]):
            try:
                norm_img = self.normalizer.normalize(x_np[i])
                normalized_batch.append(norm_img)
            except:
                # If normalization fails, use original
                normalized_batch.append(x_np[i])
        
        # Convert back to tensor
        x_norm = np.stack(normalized_batch, axis=0)
        x_norm = torch.from_numpy(x_norm).float().to(x.device) / 255.0
        x_norm = x_norm.permute(0, 3, 1, 2)  # (B, C, H, W)
        
        # Renormalize
        x_norm = (x_norm - mean) / std
        
        return x_norm
    
    def forward(self, x):
        """Forward pass with stain normalization."""
        with torch.no_grad():
            x_normalized = self.normalize_batch(x)
        
        return self.base_model(x_normalized)


def wrap_model_with_stain_normalization(model: nn.Module) -> nn.Module:
    """
    Wrap any model with Macenko stain normalization.
    
    Args:
        model: Base model
        
    Returns:
        Wrapped model with stain normalization
    """
    return StainNormalizationWrapper(model, MacenkoNormalizer())
