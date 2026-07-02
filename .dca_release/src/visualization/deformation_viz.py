"""Deformation field visualization."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import torch
import torch.nn.functional as F
from typing import List, Tuple


def create_grid_image(image_size: Tuple[int, int], grid_spacing: int = 16):
    """
    Create a regular grid image for visualization.
    
    Args:
        image_size: (H, W) tuple
        grid_spacing: Spacing between grid lines
        
    Returns:
        Grid image as numpy array
    """
    H, W = image_size
    grid = np.ones((H, W, 3), dtype=np.uint8) * 255
    
    for i in range(0, H, grid_spacing):
        grid[i, :, :] = [200, 200, 200]
    for j in range(0, W, grid_spacing):
        grid[:, j, :] = [200, 200, 200]
    
    return grid


def apply_deformation_to_grid(deformation_field, grid_spacing: int = 16):
    """
    Apply deformation field to a regular grid for visualization.
    
    Args:
        deformation_field: Tensor of shape (2, H, W) or (B, 2, H, W)
        grid_spacing: Spacing between grid lines
        
    Returns:
        Warped grid as numpy array
    """
    if deformation_field.dim() == 4:
        deformation_field = deformation_field[0]
    
    _, H, W = deformation_field.shape
    
    grid = torch.zeros((1, 3, H, W), device=deformation_field.device)
    for i in range(0, H, grid_spacing):
        grid[0, :, i, :] = 0.8
    for j in range(0, W, grid_spacing):
        grid[0, :, :, j] = 0.8
    
    deformation_norm = deformation_field.unsqueeze(0)
    deformation_norm[:, 0, :, :] = 2.0 * deformation_field[0] / (W - 1)
    deformation_norm[:, 1, :, :] = 2.0 * deformation_field[1] / (H - 1)
    
    warped_grid = F.grid_sample(grid, deformation_norm.permute(0, 2, 3, 1),
                                mode='bilinear', padding_mode='border', align_corners=True)
    
    warped_grid = warped_grid[0].permute(1, 2, 0).cpu().numpy()
    warped_grid = (warped_grid * 255).astype(np.uint8)
    
    return warped_grid


def compute_conformal_energy_map(deformation_field):
    """
    Compute conformal energy map from deformation field.
    
    Args:
        deformation_field: Tensor of shape (2, H, W) or (B, 2, H, W)
        
    Returns:
        Conformal energy map as numpy array
    """
    if deformation_field.dim() == 4:
        deformation_field = deformation_field[0]
    
    device = deformation_field.device
    phi_x = deformation_field[0:1]
    phi_y = deformation_field[1:2]
    
    dx_kernel = torch.tensor([[-1, 0, 1]], dtype=torch.float32, device=device).view(1, 1, 1, 3) / 2.0
    dy_kernel = torch.tensor([[-1], [0], [1]], dtype=torch.float32, device=device).view(1, 1, 3, 1) / 2.0
    
    phi_x_dx = F.conv2d(phi_x.unsqueeze(0), dx_kernel, padding=(0, 1))
    phi_x_dy = F.conv2d(phi_x.unsqueeze(0), dy_kernel, padding=(1, 0))
    phi_y_dx = F.conv2d(phi_y.unsqueeze(0), dx_kernel, padding=(0, 1))
    phi_y_dy = F.conv2d(phi_y.unsqueeze(0), dy_kernel, padding=(1, 0))
    
    conf_energy = (phi_x_dx - phi_y_dy)**2 + (phi_x_dy + phi_y_dx)**2
    
    conf_energy = conf_energy[0, 0].cpu().numpy()
    
    return conf_energy


def visualize_deformation_fields(images: torch.Tensor,
                                 deformation_fields: torch.Tensor,
                                 transformed_images: torch.Tensor,
                                 class_names: List[str] = None,
                                 save_path: str = None,
                                 num_samples: int = 3,
                                 grid_spacing: int = 16):
    """
    Visualize deformation fields with original and transformed images.
    
    Args:
        images: Original images (B, C, H, W)
        deformation_fields: Deformation fields (B, 2, H, W)
        transformed_images: Transformed images (B, C, H, W)
        class_names: List of class names
        save_path: Path to save figure
        num_samples: Number of samples to visualize
        grid_spacing: Grid spacing for deformation visualization
    """
    num_samples = min(num_samples, images.shape[0])
    
    fig = plt.figure(figsize=(16, 4 * num_samples))
    gs = gridspec.GridSpec(num_samples, 4, figure=fig, wspace=0.3, hspace=0.3)
    
    for idx in range(num_samples):
        img = images[idx].permute(1, 2, 0).cpu().numpy()
        img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        
        trans_img = transformed_images[idx].permute(1, 2, 0).cpu().numpy()
        trans_img = (trans_img - trans_img.min()) / (trans_img.max() - trans_img.min() + 1e-8)
        
        deform_field = deformation_fields[idx]
        warped_grid = apply_deformation_to_grid(deform_field, grid_spacing)
        conf_energy = compute_conformal_energy_map(deform_field)
        
        ax1 = fig.add_subplot(gs[idx, 0])
        ax1.imshow(img)
        ax1.set_title('Original Image', fontsize=11)
        ax1.axis('off')
        
        ax2 = fig.add_subplot(gs[idx, 1])
        ax2.imshow(warped_grid)
        ax2.set_title('Deformation Grid', fontsize=11)
        ax2.axis('off')
        
        ax3 = fig.add_subplot(gs[idx, 2])
        ax3.imshow(trans_img)
        ax3.set_title('Transformed Image', fontsize=11)
        ax3.axis('off')
        
        ax4 = fig.add_subplot(gs[idx, 3])
        im = ax4.imshow(conf_energy, cmap='RdYlBu_r', vmin=0, vmax=0.2)
        ax4.set_title('Conformal Energy Map', fontsize=11)
        ax4.axis('off')
        plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()


def visualize_semantic_adaptation(images_by_class: dict,
                                  deformations_by_class: dict,
                                  class_names: List[str],
                                  save_path: str = None):
    """
    Visualize semantic adaptation: different deformations for different tissue types.
    
    Args:
        images_by_class: Dict mapping class idx to list of images
        deformations_by_class: Dict mapping class idx to list of deformation fields
        class_names: List of class names
        save_path: Path to save figure
    """
    num_classes = len(images_by_class)
    
    fig = plt.figure(figsize=(12, 3 * num_classes))
    gs = gridspec.GridSpec(num_classes, 3, figure=fig, wspace=0.25, hspace=0.35)
    
    for cls_idx in range(num_classes):
        if cls_idx not in images_by_class:
            continue
        
        imgs = images_by_class[cls_idx]
        deforms = deformations_by_class[cls_idx]
        
        img = imgs[0].permute(1, 2, 0).cpu().numpy()
        img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        
        deform_field = deforms[0]
        warped_grid = apply_deformation_to_grid(deform_field, grid_spacing=12)
        conf_energy = compute_conformal_energy_map(deform_field)
        
        mean_displacement = torch.sqrt(deform_field[0]**2 + deform_field[1]**2).mean().item()
        mean_conf_energy = conf_energy.mean()
        
        ax1 = fig.add_subplot(gs[cls_idx, 0])
        ax1.imshow(img)
        ax1.set_ylabel(class_names[cls_idx], fontsize=12, fontweight='bold')
        if cls_idx == 0:
            ax1.set_title('Original Image', fontsize=12)
        ax1.axis('off')
        
        ax2 = fig.add_subplot(gs[cls_idx, 1])
        ax2.imshow(warped_grid)
        if cls_idx == 0:
            ax2.set_title(f'Deformation Grid\n$\\bar{{\\|\\phi\\|}}$ = {mean_displacement:.1f} px', fontsize=12)
        else:
            ax2.set_title(f'$\\bar{{\\|\\phi\\|}}$ = {mean_displacement:.1f} px', fontsize=11)
        ax2.axis('off')
        
        ax3 = fig.add_subplot(gs[cls_idx, 2])
        im = ax3.imshow(conf_energy, cmap='RdYlBu_r', vmin=0, vmax=0.15)
        if cls_idx == 0:
            ax3.set_title(f'Conformal Energy\n$\\bar{{E}}_{{conf}}$ = {mean_conf_energy:.3f}', fontsize=12)
        else:
            ax3.set_title(f'$\\bar{{E}}_{{conf}}$ = {mean_conf_energy:.3f}', fontsize=11)
        ax3.axis('off')
        plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.savefig(save_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    
    plt.close()
