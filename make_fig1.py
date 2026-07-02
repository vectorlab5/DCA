import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import numpy as np
from figtools import CLASSES, CLASS_FULL, sample_tiles, imshow_tile, panel_label, CB
from paperdata import PER_CLASS

fig = plt.figure(figsize=(7.2, 9.0))
gs = GridSpec(4, 9, figure=fig, height_ratios=[1.0, 1.25, 1.5, 1.15],
              hspace=0.55, wspace=0.18,
              left=0.08, right=0.97, top=0.93, bottom=0.03)

def band_title(ax_ref, text, dy=0.018, letter=None, x_override=None):
    """Place a left-aligned band header above the given axis, using real position.
    Letter sits at the far left; title text starts a fixed gap to its right."""
    pos = ax_ref.get_position()
    letter_x = (x_override if x_override is not None else pos.x0) - 0.0 if x_override is not None else pos.x0-0.055
    letter_x = 0.025 if x_override is not None else pos.x0-0.055
    title_x = (letter_x + 0.045) if letter else (x_override if x_override is not None else pos.x0)
    y = pos.y1 + dy
    if letter:
        fig.text(letter_x, y, letter, ha="left", va="bottom", fontsize=12, fontweight="bold")
    fig.text(title_x, y, text, ha="left", va="bottom", fontsize=8.4, fontweight="bold")

# ---- Panel a: 9-class H&E gallery ----
axes_a=[]
for j,c in enumerate(CLASSES):
    ax = fig.add_subplot(gs[0, j]); axes_a.append(ax)
    tiles,_ = sample_tiles(c, n=1, seed=7)
    imshow_tile(ax, tiles[0])
    ax.set_title(c, fontsize=7.2, pad=2, fontweight="bold")

# ---- Panel b: intra-class heterogeneity ----
gb = gs[1, 0:4].subgridspec(2, 4, hspace=0.06, wspace=0.06)
tum,_ = sample_tiles("TUM", n=4, seed=3)
bak,_ = sample_tiles("BACK", n=4, seed=3)
ax_b_first=None
for i,img in enumerate(tum):
    ax=fig.add_subplot(gb[0,i]); imshow_tile(ax,img)
    if i==0:
        ax_b_first=ax
        ax.set_ylabel("TUM\nMV 0.81", fontsize=6.3, rotation=0, ha="right", va="center", labelpad=8)
for i,img in enumerate(bak):
    ax=fig.add_subplot(gb[1,i]); imshow_tile(ax,img)
    if i==0:
        ax.set_ylabel("BACK\nMV 0.18", fontsize=6.3, rotation=0, ha="right", va="center", labelpad=8)

# ---- Panel e: morphological variability bar chart ----
axe = fig.add_subplot(gs[1, 5:9])
mv = [PER_CLASS[c][4] for c in CLASSES]
order = np.argsort(mv)
cls_o = [CLASSES[i] for i in order]; mv_o=[mv[i] for i in order]
colors = plt.cm.viridis(np.array(mv_o)/max(mv_o))
axe.barh(range(len(cls_o)), mv_o, color=colors, edgecolor="black", linewidth=0.5)
axe.set_yticks(range(len(cls_o))); axe.set_yticklabels(cls_o, fontsize=6.5)
axe.set_xlabel("Morphological variability (MV)", fontsize=7)
axe.tick_params(labelsize=6.5)
for i,v in enumerate(mv_o):
    axe.text(v+0.012, i, f"{v:.2f}", va="center", fontsize=5.8)
axe.set_xlim(0, 0.95); axe.margins(y=0.02)

# ---- Panel c: DCA architecture schematic ----
axc = fig.add_subplot(gs[2, 0:9])
arch = mpimg.imread("architecture.png")
axc.imshow(arch); axc.axis("off")

# ---- Panel d: conformal-normalization concept (clean interior crops) ----
viz = mpimg.imread("visualization.png")
# TUM row (row0), tight cell bounds detected from content bbox (no white margins)
tum_orig = viz[90:581, 94:586]      # col0 Original
tum_tran = viz[90:581, 1276:1768]   # col2 Transformed
gd = gs[3, 0:5].subgridspec(1, 2, wspace=0.14)
ax_d0=fig.add_subplot(gd[0,0]); imshow_tile(ax_d0, tum_orig); ax_d0.set_title("Original H&E (tumour)", fontsize=6.8, pad=2)
ax_d1=fig.add_subplot(gd[0,1]); imshow_tile(ax_d1, tum_tran); ax_d1.set_title("Conformally normalized", fontsize=6.8, pad=2)
# arrow between
ax_d0.annotate("", xy=(1.13,0.5), xytext=(1.0,0.5), xycoords="axes fraction",
               arrowprops=dict(arrowstyle="-|>", lw=1.3, color=CB["vermillion"]))

# ---- Panel f: study design flow ----
axf = fig.add_subplot(gs[3, 6:9]); axf.axis("off")
steps = ["100,000 H&E tiles\n(NCT-CRC-HE-100K)","DCA geometric\nnormalization",
         "9-class tissue\nclassification","External validation\nCRC-VAL-HE-7K (7,180)"]
ys = np.linspace(0.90, 0.08, len(steps))
for i,(s,y) in enumerate(zip(steps,ys)):
    axf.annotate(s, xy=(0.5,y), xycoords="axes fraction", ha="center", va="center",
                 fontsize=6.0, bbox=dict(boxstyle="round,pad=0.28",
                 fc=CB["skyblue"] if i%2==0 else CB["yellow"], ec="black", lw=0.5))
    if i<len(steps)-1:
        axf.annotate("", xy=(0.5,ys[i+1]+0.085), xytext=(0.5,y-0.085), xycoords="axes fraction",
                     arrowprops=dict(arrowstyle="-|>", lw=0.9, color="black"))

# ---- Band titles (placed from real positions) ----
fig.canvas.draw()
band_title(axes_a[0], "Nine colorectal tissue classes (H&E, 224×224 px)", letter="a", x_override=0.08)
band_title(ax_b_first, "Intra-class heterogeneity", letter="b")
band_title(axe, "Per-class tissue heterogeneity", letter="e")
band_title(axc, "Deep Conformal Alignment — end-to-end architecture", letter="c", x_override=0.08)
band_title(ax_d0, "Conformal normalization on real tissue", letter="d", x_override=0.08)
band_title(axf, "Study design", letter="f")

fig.savefig("Fig1_overview.png", dpi=400, bbox_inches="tight")
fig.savefig("Fig1_overview.pdf", bbox_inches="tight")
print("saved Fig1_overview v2")
