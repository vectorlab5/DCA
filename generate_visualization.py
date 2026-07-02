"""
Generate Fig 5: Visualization of learned deformation fields for different tissue types.
Shows (a) original image, (b) deformation grid, (c) transformed image, (d) conformal energy map.
"""
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
sys.path.append('src')
from model import DCANet
from dataset import HistopathologyDataset, get_transforms

def compute_conformal_energy(phi):
    u, v = phi[:, 0:1, :, :], phi[:, 1:2, :, :]
    du_dx = (u[:, :, :, 2:] - u[:, :, :, :-2]) / 2
    du_dy = (u[:, :, 2:, :] - u[:, :, :-2, :]) / 2
    dv_dx = (v[:, :, :, 2:] - v[:, :, :, :-2]) / 2
    dv_dy = (v[:, :, 2:, :] - v[:, :, :-2, :]) / 2
    h, w = min(du_dx.shape[2], du_dy.shape[2]), min(du_dx.shape[3], du_dy.shape[3])
    du_dx, du_dy = du_dx[:, :, :h, :w], du_dy[:, :, :h, :w]
    dv_dx, dv_dy = dv_dx[:, :, :h, :w], dv_dy[:, :, :h, :w]
    return ((du_dx - dv_dy)**2 + (du_dy + dv_dx)**2).squeeze()

def draw_deformation_grid(phi, img_size=224, grid_spacing=16):
    H, W = img_size, img_size
    phi_np = phi.cpu().numpy()
    if phi_np.shape[1] != H or phi_np.shape[2] != W:
        phi_resized = np.zeros((2, H, W))
        for c in range(2):
            phi_resized[c] = np.array(Image.fromarray(phi_np[c]).resize((W, H), Image.BILINEAR))
        phi_np = phi_resized
    
    grid_img = np.ones((H, W, 3), dtype=np.uint8) * 255
    for y in range(0, H, grid_spacing):
        for x in range(W - 1):
            x1, y1 = int(x + phi_np[0, y, x] * W / 2), int(y + phi_np[1, y, x] * H / 2)
            x2, y2 = int(x + 1 + phi_np[0, y, x + 1] * W / 2), int(y + phi_np[1, y, x + 1] * H / 2)
            x1, y1, x2, y2 = np.clip([x1, y1, x2, y2], 0, [W-1, H-1, W-1, H-1])
            for t in np.linspace(0, 1, 20):
                px, py = int(x1 + t*(x2-x1)), int(y1 + t*(y2-y1))
                if 0 <= px < W and 0 <= py < H:
                    grid_img[py, px] = [0, 0, 200]
    for x in range(0, W, grid_spacing):
        for y in range(H - 1):
            x1, y1 = int(x + phi_np[0, y, x] * W / 2), int(y + phi_np[1, y, x] * H / 2)
            x2, y2 = int(x + phi_np[0, y + 1, x] * W / 2), int(y + 1 + phi_np[1, y + 1, x] * H / 2)
            x1, y1, x2, y2 = np.clip([x1, y1, x2, y2], 0, [W-1, H-1, W-1, H-1])
            for t in np.linspace(0, 1, 20):
                px, py = int(x1 + t*(x2-x1)), int(y1 + t*(y2-y1))
                if 0 <= px < W and 0 <= py < H:
                    grid_img[py, px] = [0, 0, 200]
    return grid_img

def unnormalize(tensor):
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    return (tensor * std + mean).clamp(0, 1)

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = DCANet(num_classes=9, backbone='resnet18').to(device)
    checkpoint = torch.load('checkpoints/frac_0.1/checkpoint_epoch_5.pth', map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    transform = get_transforms(img_size=224, split='test')
    dataset = HistopathologyDataset('data', split='test', transform=transform)
    classes = dataset.classes
    
    # Target tissue types: TUM (aggressive), NORM (subtle), MUS (smooth)
    target_classes = ['TUM', 'NORM', 'MUS']
    target_indices = {cls: classes.index(cls) for cls in target_classes}
    
    print("Finding correctly classified samples for each tissue type...")
    selected = {cls: None for cls in target_classes}
    
    with torch.no_grad():
        for idx in range(len(dataset)):
            if all(v is not None for v in selected.values()):
                break
            img, label = dataset[idx]
            cls_name = classes[label]
            if cls_name not in target_classes or selected[cls_name] is not None:
                continue
            
            img_batch = img.unsqueeze(0).to(device)
            logits, warped, phi, v = model(img_batch)
            pred = logits.argmax(dim=1).item()
            
            if pred == label:  # Correctly classified
                energy = compute_conformal_energy(phi.cpu().unsqueeze(0)).mean().item()
                selected[cls_name] = (img, phi.cpu(), warped.cpu(), energy)
                print(f"  Found {cls_name} (energy={energy:.4f})")
    
    # Create figure
    fig, axes = plt.subplots(3, 4, figsize=(10, 7.5))
    col_titles = ['(a) Original', '(b) Deformation Grid', '(c) Transformed', '(d) Conformal Energy']
    
    for i, cls_name in enumerate(target_classes):
        img, phi, warped, energy = selected[cls_name]
        phi_sq = phi.squeeze()
        
        img_np = unnormalize(img).permute(1, 2, 0).numpy()
        axes[i, 0].imshow(img_np)
        axes[i, 0].set_xticks([])
        axes[i, 0].set_yticks([])
        for spine in axes[i, 0].spines.values():
            spine.set_visible(False)
        axes[i, 0].set_ylabel(cls_name, fontsize=11, fontweight='bold', rotation=90, labelpad=10, va='center')
        
        grid_img = draw_deformation_grid(phi_sq, img_size=224, grid_spacing=14)
        axes[i, 1].imshow(grid_img)
        axes[i, 1].axis('off')
        
        warped_np = unnormalize(warped.squeeze()).permute(1, 2, 0).numpy()
        axes[i, 2].imshow(warped_np)
        axes[i, 2].axis('off')
        
        energy_map = compute_conformal_energy(phi_sq.unsqueeze(0)).numpy()
        while energy_map.ndim > 2:
            energy_map = energy_map.squeeze(0)
        energy_map = np.array(Image.fromarray(energy_map.astype(np.float32)).resize((224, 224), Image.BILINEAR))
        im = axes[i, 3].imshow(energy_map, cmap='coolwarm', vmin=0, vmax=0.15)
        axes[i, 3].axis('off')
    
    for j, title in enumerate(col_titles):
        axes[0, j].set_title(title, fontsize=11, fontweight='bold')
    
    plt.subplots_adjust(right=0.88)
    cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Conformal Energy', fontsize=10)
    
    plt.savefig('visualization.pdf', format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig('visualization.png', format='png', bbox_inches='tight', dpi=300)
    print("Saved visualization.pdf and visualization.png")

if __name__ == '__main__':
    main()
