import torch
import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_results(images, warped_images, phi, save_path, epoch):
    """
    Visualizes original images, warped images, and deformation fields.
    """
    B = images.shape[0]
    n_samples = min(B, 4)
    
    fig, axes = plt.subplots(n_samples, 3, figsize=(12, 4*n_samples))
    
    # Normalize images for display
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(images.device)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(images.device)
    
    images_disp = images * std + mean
    warped_disp = warped_images * std + mean
    
    images_disp = torch.clamp(images_disp, 0, 1)
    warped_disp = torch.clamp(warped_disp, 0, 1)
    
    for i in range(n_samples):
        # Original
        ax = axes[i, 0] if n_samples > 1 else axes[0]
        ax.imshow(images_disp[i].permute(1, 2, 0).detach().cpu().numpy())
        ax.set_title("Original")
        ax.axis('off')
        
        # Warped
        ax = axes[i, 1] if n_samples > 1 else axes[1]
        ax.imshow(warped_disp[i].permute(1, 2, 0).detach().cpu().numpy())
        ax.set_title("Warped")
        ax.axis('off')
        
        # Deformation Field (Magnitude)
        ax = axes[i, 2] if n_samples > 1 else axes[2]
        phi_mag = torch.norm(phi[i], dim=0).detach().cpu().numpy()
        im = ax.imshow(phi_mag, cmap='jet')
        ax.set_title("Deformation Magnitude")
        ax.axis('off')
        plt.colorbar(im, ax=ax)
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    plt.close()

def save_checkpoint(model, optimizer, epoch, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"checkpoint_epoch_{epoch}.pth")
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, path)
