import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import numpy as np
from figtools import imshow_tile, panel_label, CB
from paperdata import DEFORM, DEFORM_DELTA_R, CONF_ENERGY_BLUE_FRAC, PER_CLASS

viz = mpimg.imread("visualization.png")
# detected cell bounds (rows x cols)
ROWS = {"TUM":(90,581), "NORM":(701,1193), "MUS":(1313,1804)}
COLS = {"Original":(94,586), "Grid":(704,1177), "Transformed":(1276,1768), "Energy":(1867,2359)}
COL_TITLES = {"Original":"Original H&E","Grid":"Deformation field φ","Transformed":"Normalized tissue","Energy":"Conformal energy"}

def cell(row,col):
    r0,r1=ROWS[row]; c0,c1=COLS[col]
    return viz[r0:r1, c0:c1]

fig = plt.figure(figsize=(7.2, 8.2))
gs = GridSpec(4, 4, figure=fig, height_ratios=[1,1,1,1.15], hspace=0.28, wspace=0.12,
              left=0.10, right=0.90, top=0.90, bottom=0.07)

# ---- Panels a-c: 3 tissue rows x 4 columns of real DCA outputs ----
tissues=["TUM","NORM","MUS"]
disp={"TUM":18.2,"NORM":9.4,"MUS":5.1}; en={"TUM":0.087,"NORM":0.042,"MUS":0.021}
letters=["a","b","c"]
for ri,t in enumerate(tissues):
    for ci,col in enumerate(COLS):
        ax=fig.add_subplot(gs[ri,ci])
        img=cell(t,col)
        if col=="Energy":
            ax.imshow(img)
        else:
            ax.imshow(img)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_linewidth(0.6)
        if ri==0:
            ax.set_title(COL_TITLES[col], fontsize=7.2, pad=3, fontweight="bold")
        if ci==0:
            ax.set_ylabel(f"{t}", fontsize=8, fontweight="bold", rotation=0, ha="right", va="center", labelpad=14)
            panel_label(ax, letters[ri], x=-0.42, y=1.05)
        if ci==2:  # annotate transformed with real deform stats
            ax.text(0.5,-0.09, f"$\\bar{{\\|\\phi\\|}}$={disp[t]} px", transform=ax.transAxes,
                    ha="center", va="top", fontsize=6.3, color=CB["vermillion"])
        if ci==3:
            ax.text(0.5,-0.09, f"$\\bar{{\\mathcal{{E}}}}$={en[t]:.3f}", transform=ax.transAxes,
                    ha="center", va="top", fontsize=6.3, color=CB["blue"])

# shared colourbar for energy column
import matplotlib as mpl
from matplotlib.cm import ScalarMappable
sm=ScalarMappable(norm=mpl.colors.Normalize(0,0.15), cmap="coolwarm")
cax=fig.add_axes([0.915, 0.50, 0.017, 0.38])
cb=fig.colorbar(sm, cax=cax); cb.set_label("Conformal energy $\\mathcal{E}_{conf}$", fontsize=6.8)
cb.ax.tick_params(labelsize=6)

# ---- Panel d: deformation magnitude per tissue (bar) ----
axd=fig.add_subplot(gs[3,0])
ts=["MUS","NORM","TUM"]; vals=[DEFORM[t][0] for t in ts]
cols_d=[CB["green"],CB["orange"],CB["vermillion"]]
axd.bar(ts, vals, color=cols_d, edgecolor="black", linewidth=0.5, width=0.62)
for i,v in enumerate(vals): axd.text(i,v+0.3,f"{v}",ha="center",fontsize=6.5)
axd.set_ylabel("Mean displacement (px)", fontsize=7)
axd.set_title("Deformation", fontsize=7.4, fontweight="bold", pad=3)
axd.tick_params(labelsize=6.8); axd.set_ylim(0,21)
panel_label(axd,"d",x=-0.34,y=1.15)

# ---- Panel e: conformal energy per tissue (bar) ----
axe=fig.add_subplot(gs[3,1])
valse=[DEFORM[t][1] for t in ts]
axe.bar(ts, valse, color=cols_d, edgecolor="black", linewidth=0.5, width=0.62)
for i,v in enumerate(valse): axe.text(i,v+0.002,f"{v:.3f}",ha="center",fontsize=6.3)
axe.set_ylabel("Mean conformal energy", fontsize=7)
axe.set_title("Angle distortion", fontsize=7.4, fontweight="bold", pad=3)
axe.tick_params(labelsize=6.8); axe.set_ylim(0,0.10)
panel_label(axe,"e",x=-0.40,y=1.15)

# ---- Panel f: deformation magnitude vs accuracy gain (scatter, r=0.91) ----
axf=fig.add_subplot(gs[3,2])
# use per-class delta accuracy vs a displacement proxy: we only have 3 measured; show measured pts + trend
# Plot the 3 measured tissues (disp vs delta-acc from PER_CLASS)
dd=[(DEFORM[t][0], PER_CLASS[t][3]) for t in ["TUM","NORM","MUS"]]
xs=[d[0] for d in dd]; ys=[d[1] for d in dd]
axf.scatter(xs,ys,s=45,c=cols_d[::-1],edgecolor="black",linewidth=0.6,zorder=3)
for (x,y),t in zip(dd,["TUM","NORM","MUS"]):
    axf.annotate(t,(x,y),fontsize=6,xytext=(4,3),textcoords="offset points")
axf.set_xlabel("Mean displacement (px)", fontsize=7)
axf.set_ylabel("Δ Accuracy (pp)", fontsize=7)
axf.set_title(f"Adaptivity (r={DEFORM_DELTA_R})", fontsize=7.4, fontweight="bold", pad=3)
axf.tick_params(labelsize=6.8); axf.margins(0.15)
panel_label(axf,"f",x=-0.40,y=1.15)

# ---- Panel g: angle-preservation summary (text stat) ----
axg=fig.add_subplot(gs[3,3]); axg.axis("off")
panel_label(axg,"g",x=-0.08,y=1.15)
axg.text(0.5,0.72,f"{CONF_ENERGY_BLUE_FRAC}%", ha="center",va="center",fontsize=22,
         fontweight="bold", color=CB["blue"], transform=axg.transAxes)
axg.text(0.5,0.44,"of pixels have\n$\\mathcal{E}_{conf}<0.10$", ha="center",va="center",
         fontsize=7, transform=axg.transAxes)
axg.text(0.5,0.16,"→ transformations are\nquasiconformal\n(angle-preserving)", ha="center",va="center",
         fontsize=6.4, color="dimgray", transform=axg.transAxes)

fig.savefig("Fig2_normalization.png", dpi=400, bbox_inches="tight")
fig.savefig("Fig2_normalization.pdf", bbox_inches="tight")
print("saved Fig2_normalization")
