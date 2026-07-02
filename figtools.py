"""Shared helpers for npj DCA figure generation. Real CRC-VAL-HE-7K tiles."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

DATA = "/Users/xiufengliu/Projects/datasets/colorectal_histology"
# Clinical names for the 9 NCT-CRC tissue classes
CLASS_FULL = {
    "ADI":"Adipose", "BACK":"Background", "DEB":"Debris",
    "LYM":"Lymphocytes", "MUC":"Mucus", "MUS":"Smooth muscle",
    "NORM":"Normal mucosa", "STR":"Cancer-assoc. stroma", "TUM":"Tumour epithelium",
}
CLASSES = ["ADI","BACK","DEB","LYM","MUC","MUS","NORM","STR","TUM"]

# npj / Nature publication style
plt.rcParams.update({
    "font.family":"DejaVu Sans", "font.size":8,
    "axes.linewidth":0.8, "axes.titlesize":9, "axes.labelsize":8,
    "xtick.labelsize":7, "ytick.labelsize":7, "legend.fontsize":7,
    "figure.dpi":150, "savefig.dpi":400, "savefig.bbox":"tight",
    "axes.spines.top":False, "axes.spines.right":False,
    "pdf.fonttype":42, "ps.fonttype":42,
})
# Colourblind-safe palette (Okabe-Ito) for methods
CB = {"black":"#000000","orange":"#E69F00","skyblue":"#56B4E9","green":"#009E73",
      "yellow":"#F0E442","blue":"#0072B2","vermillion":"#D55E00","purple":"#CC79A7","grey":"#999999"}

def list_tiles(cls):
    d = os.path.join(DATA, cls)
    return sorted([os.path.join(d,f) for f in os.listdir(d) if f.endswith(".tif")])

def load_tile(path):
    return np.array(Image.open(path))

def sample_tiles(cls, n=1, seed=0):
    rng = np.random.RandomState(seed)
    files = list_tiles(cls)
    idx = rng.choice(len(files), size=min(n,len(files)), replace=False)
    return [load_tile(files[i]) for i in idx], [files[i] for i in idx]

def panel_label(ax, letter, x=-0.08, y=1.06, fs=11):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=fs,
            fontweight="bold", va="top", ha="right")

def imshow_tile(ax, img, title=None, title_fs=8):
    ax.imshow(img); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.6)
    if title: ax.set_title(title, fontsize=title_fs, pad=2)

if __name__ == "__main__":
    # Contact sheet: 3 tiles x 9 classes verifying every class loads
    fig, axes = plt.subplots(3, 9, figsize=(13.5, 4.6))
    for j,c in enumerate(CLASSES):
        tiles,_ = sample_tiles(c, n=3, seed=42)
        for i in range(3):
            imshow_tile(axes[i,j], tiles[i], title=(f"{c}\n{CLASS_FULL[c]}" if i==0 else None), title_fs=7)
    fig.suptitle("CRC-VAL-HE-7K — representative H&E tiles per tissue class (real data)", fontsize=10, y=1.01)
    fig.tight_layout()
    fig.savefig("contact_sheet.png", dpi=200)
    print("saved contact_sheet.png")
