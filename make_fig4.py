import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from figtools import panel_label, CB, sample_tiles, imshow_tile
from paperdata import (FRACTIONS, DATA_EFF, DATA_EFF_RATIO, GENERALIZATION, HEADLINE)

fig = plt.figure(figsize=(7.2, 7.6))
gs = GridSpec(3, 6, figure=fig, height_ratios=[1.25,1.1,1.0], hspace=0.52, wspace=1.1,
              left=0.09, right=0.97, top=0.93, bottom=0.07)

mcol={"ResNet-18":CB["grey"],"STN-TPS":CB["skyblue"],"CEM":CB["green"],
      "SimCLR+FT":CB["purple"],"UNI (FT)":CB["blue"],"DCA":CB["vermillion"],"DCA+UNI":CB["orange"]}

# ---- Panel a: learning curves (accuracy vs data fraction) ----
axa=fig.add_subplot(gs[0,0:3])
for m,pts in DATA_EFF.items():
    acc=[p[0] for p in pts]; err=[p[1] for p in pts]
    axa.errorbar(FRACTIONS, acc, yerr=err, marker="o", ms=3, lw=1.1, capsize=1.5,
                 color=mcol[m], label=m)
axa.set_xscale("log"); axa.set_xticks(FRACTIONS); axa.set_xticklabels([f"{f}%" for f in FRACTIONS], fontsize=6.5)
axa.set_xlabel("Labeled training data", fontsize=7.5)
axa.set_ylabel("Accuracy (%)", fontsize=7.5)
axa.legend(fontsize=5.4, loc="lower right", frameon=False, ncol=2)
axa.tick_params(labelsize=6.5); axa.grid(alpha=0.25, lw=0.4)
axa.set_title("Data-efficiency learning curves", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axa,"a",x=-0.13,y=1.05)

# ---- Panel b: 4.2x efficiency illustration ----
axb=fig.add_subplot(gs[0,3:6])
# DCA at 10% vs the fraction where the PLOTTED ResNet curve reaches the same accuracy.
# Crossing derived by interpolating the ResNet points in log-x (matches the log x-axis).
rn=[p[0] for p in DATA_EFF["ResNet-18"]]; dca=[p[0] for p in DATA_EFF["DCA"]]
axb.plot(FRACTIONS, rn, marker="s", ms=3.5, color=CB["grey"], lw=1.2, label="ResNet-18")
axb.plot(FRACTIONS, dca, marker="o", ms=3.5, color=CB["vermillion"], lw=1.2, label="DCA")
axb.set_xscale("log"); axb.set_xticks(FRACTIONS); axb.set_xticklabels([f"{f}%" for f in FRACTIONS], fontsize=6.5)
dca10=DATA_EFF["DCA"][1][0]
# invert ResNet acc->fraction in log-x space at y=dca10 (ResNet is monotonic increasing)
logx_cross=np.interp(dca10, rn, np.log10(FRACTIONS))
x_cross=10**logx_cross
axb.axhline(dca10, color="black", ls=":", lw=0.7)
axb.scatter([x_cross],[dca10], s=40, marker="s", color=CB["grey"], zorder=5,
            edgecolor="black", linewidth=0.5)
axb.annotate(f"DCA @10% = {dca10}%", xy=(10,dca10), xytext=(10.5,dca10-11), fontsize=6,
             arrowprops=dict(arrowstyle="->",lw=0.7))
axb.annotate(f"ResNet-18 reaches this\nonly at ≈{x_cross:.0f}% data", xy=(x_cross,dca10),
             xytext=(13,dca10+7), fontsize=6,
             arrowprops=dict(arrowstyle="->",lw=0.7,color=CB["grey"]))
axb.scatter([10],[dca10], s=45, color=CB["vermillion"], zorder=5, edgecolor="black", linewidth=0.5)
axb.set_xlabel("Labeled training data", fontsize=7.5); axb.set_ylabel("Accuracy (%)", fontsize=7.5)
axb.legend(fontsize=6, loc="lower right", frameon=False)
axb.tick_params(labelsize=6.5); axb.grid(alpha=0.25, lw=0.4)
axb.set_title("Fewer labels for equal accuracy", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axb,"b",x=-0.13,y=1.05)

# ---- Panel c: cross-dataset generalization (source vs target grouped) ----
axc=fig.add_subplot(gs[1,0:3])
gm=list(GENERALIZATION.keys()); x=np.arange(len(gm)); w=0.38
src=[GENERALIZATION[m][0] for m in gm]; tgt=[GENERALIZATION[m][1] for m in gm]
axc.bar(x-w/2, src, w, label="Source (100K)", color=CB["skyblue"], edgecolor="black", linewidth=0.4)
axc.bar(x+w/2, tgt, w, label="External (7K)", color=CB["vermillion"], edgecolor="black", linewidth=0.4)
axc.set_xticks(x); axc.set_xticklabels(gm, fontsize=5.6, rotation=35, ha="right")
axc.set_ylabel("Accuracy (%)", fontsize=7.5); axc.set_ylim(80,97)
axc.legend(fontsize=5.8, loc="upper left", frameon=False)
axc.tick_params(labelsize=6.3)
axc.set_title("Cross-dataset generalization", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axc,"c",x=-0.13,y=1.06)

# ---- Panel d: generalization gap (drop) ----
axd=fig.add_subplot(gs[1,3:6])
drops=[abs(GENERALIZATION[m][2]) for m in gm]
order=np.argsort(drops)[::-1]
gm_o=[gm[i] for i in order]; dr_o=[drops[i] for i in order]
cols_d=[CB["vermillion"] if "DCA" in m else CB["grey"] for m in gm_o]
axd.barh(range(len(gm_o))[::-1], dr_o, color=cols_d, edgecolor="black", linewidth=0.4)
axd.set_yticks(range(len(gm_o))[::-1]); axd.set_yticklabels(gm_o, fontsize=5.8)
axd.set_xlabel("Accuracy drop (pp)", fontsize=7.5)
for i,v in enumerate(dr_o): axd.text(v+0.05, len(gm_o)-1-i, f"−{v}", va="center", fontsize=5.8)
axd.set_xlim(0,5.6)
axd.tick_params(labelsize=6.3)
axd.set_title("Domain-shift robustness\n(smaller = better)", fontsize=7.4, fontweight="bold", pad=3)
panel_label(axd,"d",x=-0.30,y=1.10)

# ---- Panel e: external-validation tiles (real CRC-VAL-HE-7K) ----
ge = gs[2,0:4].subgridspec(2,4,hspace=0.12,wspace=0.06)
from figtools import CLASSES, CLASS_FULL
show=["TUM","STR","LYM","DEB"]
for ci,c in enumerate(show):
    tiles,_=sample_tiles(c,n=2,seed=11)
    for ri in range(2):
        ax=fig.add_subplot(ge[ri,ci]); imshow_tile(ax,tiles[ri])
        if ri==0: ax.set_title(c, fontsize=6.6, fontweight="bold", pad=1.5)
        if ci==0 and ri==0: panel_label(ax,"e",x=-0.30,y=1.35)
fig.text(0.09, 0.285, "External validation set — CRC-VAL-HE-7K (7,180 tiles, unseen)",
         fontsize=7.4, fontweight="bold", ha="left")

# ---- Panel f: headline efficiency stat ----
axf=fig.add_subplot(gs[2,4:6]); axf.axis("off")
axf.text(0.5,0.82,f"up to {DATA_EFF_RATIO}×", ha="center", fontsize=21, fontweight="bold",
         color=CB["vermillion"], transform=axf.transAxes)
axf.text(0.5,0.60,"fewer labels for\nequivalent accuracy", ha="center", fontsize=7,
         transform=axf.transAxes)
axf.text(0.5,0.34,f"DCA reaches {DATA_EFF['DCA'][1][0]}% using 10% of labels;\n"
         f"ResNet-18 needs ~33% for the same\n(reported peak efficiency {DATA_EFF_RATIO}×)",
         ha="center", fontsize=5.8, color="dimgray", transform=axf.transAxes)
panel_label(axf,"f",x=0.0,y=1.05)

fig.savefig("Fig4_efficiency.png", dpi=400, bbox_inches="tight")
fig.savefig("Fig4_efficiency.pdf", bbox_inches="tight")
print("saved Fig4_efficiency")
