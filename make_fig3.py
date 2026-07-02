import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import numpy as np
from figtools import panel_label, CB
from paperdata import (MAIN_RESULTS, FOUNDATION, DCA_METHODS, PER_CLASS, CLASSES,
                       MV_DELTA_R, FAILURES)

fig = plt.figure(figsize=(7.2, 9.2))
gs = GridSpec(3, 6, figure=fig, height_ratios=[1.5, 1.15, 1.0], hspace=0.5, wspace=0.9,
              left=0.16, right=0.97, top=0.95, bottom=0.06)

# ---- Panel a: method comparison dot-plot (all 21 methods) ----
axa = fig.add_subplot(gs[0, 0:3])
methods = list(MAIN_RESULTS.keys())
# sort by accuracy ascending for readability
methods_sorted = sorted(methods, key=lambda m: MAIN_RESULTS[m][0])
accs=[MAIN_RESULTS[m][0] for m in methods_sorted]
errs=[MAIN_RESULTS[m][1] for m in methods_sorted]
def mcolor(m):
    if m in DCA_METHODS: return CB["vermillion"]
    if m in FOUNDATION: return CB["blue"]
    return CB["grey"]
cols=[mcolor(m) for m in methods_sorted]
y=np.arange(len(methods_sorted))
axa.errorbar(accs, y, xerr=errs, fmt="none", ecolor="black", elinewidth=0.6, capsize=1.5, zorder=2)
axa.scatter(accs, y, c=cols, s=26, edgecolor="black", linewidth=0.5, zorder=3)
axa.set_yticks(y); axa.set_yticklabels(methods_sorted, fontsize=5.6)
axa.set_xlabel("Accuracy (%)", fontsize=7.5)
axa.set_xlim(86, 96)
axa.tick_params(labelsize=6.5)
axa.axvline(MAIN_RESULTS["DCA (Ours)"][0], color=CB["vermillion"], ls="--", lw=0.6, alpha=0.6, zorder=1)
# legend
from matplotlib.lines import Line2D
leg=[Line2D([0],[0],marker='o',color='w',markerfacecolor=CB["vermillion"],markersize=5,label='DCA (ours)'),
     Line2D([0],[0],marker='o',color='w',markerfacecolor=CB["blue"],markersize=5,label='Foundation/SSL'),
     Line2D([0],[0],marker='o',color='w',markerfacecolor=CB["grey"],markersize=5,label='Other baselines')]
axa.legend(handles=leg, fontsize=5.5, loc="lower right", frameon=False)
axa.set_title("Classification accuracy (5-fold CV)", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axa,"a",x=-0.42,y=1.04)

# ---- Panel b: per-class grouped bars ResNet/STN/DCA ----
axb = fig.add_subplot(gs[0, 3:6])
x=np.arange(len(CLASSES)); w=0.26
r=[PER_CLASS[c][0] for c in CLASSES]; s=[PER_CLASS[c][1] for c in CLASSES]; d=[PER_CLASS[c][2] for c in CLASSES]
axb.bar(x-w, r, w, label="ResNet-18", color=CB["grey"], edgecolor="black", linewidth=0.4)
axb.bar(x,   s, w, label="STN-TPS", color=CB["skyblue"], edgecolor="black", linewidth=0.4)
axb.bar(x+w, d, w, label="DCA", color=CB["vermillion"], edgecolor="black", linewidth=0.4)
axb.set_xticks(x); axb.set_xticklabels(CLASSES, fontsize=6, rotation=45, ha="right")
axb.set_ylabel("Accuracy (%)", fontsize=7.5); axb.set_ylim(75,101)
axb.legend(fontsize=5.8, loc="lower right", frameon=False, ncol=1)
axb.tick_params(labelsize=6.5)
axb.set_title("Per-class accuracy", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axb,"b",x=-0.20,y=1.04)

# ---- Panel c: confusion matrices (embed real output) ----
axc = fig.add_subplot(gs[1, 0:6])
cm = mpimg.imread("confusion_matrix.png")
axc.imshow(cm); axc.axis("off")
axc.set_title("Confusion matrices: ResNet-18 (left) vs DCA (right)", fontsize=7.8, fontweight="bold", pad=2)
panel_label(axc,"c",x=0.0,y=1.02)

# ---- Panel d: MV vs delta-accuracy (r=0.94) ----
axd = fig.add_subplot(gs[2, 0:2])
mv=[PER_CLASS[c][4] for c in CLASSES]; da=[PER_CLASS[c][3] for c in CLASSES]
axd.scatter(mv, da, c=plt.cm.viridis(np.array(mv)/max(mv)), s=38, edgecolor="black", linewidth=0.5, zorder=3)
# trend line
z=np.polyfit(mv,da,1); xx=np.linspace(min(mv),max(mv),50)
axd.plot(xx, np.polyval(z,xx), color="black", lw=0.8, ls="--", zorder=2)
for c in ["TUM","STR","BACK"]:
    axd.annotate(c,(PER_CLASS[c][4],PER_CLASS[c][3]),fontsize=5.6,xytext=(3,2),textcoords="offset points")
axd.set_xlabel("Morphological variability", fontsize=7)
axd.set_ylabel("Δ Accuracy (pp)", fontsize=7)
axd.set_title(f"Gain scales with\nheterogeneity (r={MV_DELTA_R})", fontsize=7, fontweight="bold", pad=3)
axd.tick_params(labelsize=6.3); axd.margins(0.12)
panel_label(axd,"d",x=-0.34,y=1.16)

# ---- Panel e: confusion-pair reductions (failure modes) ----
axe = fig.add_subplot(gs[2, 2:4])
labs=[f[0].replace(" confusion","") for f in FAILURES[:3]]
cnts=[f[1] for f in FAILURES[:3]]
axe.barh(range(len(labs))[::-1], cnts, color=CB["orange"], edgecolor="black", linewidth=0.5)
axe.set_yticks(range(len(labs))[::-1]); axe.set_yticklabels(labs, fontsize=6)
axe.set_xlabel("Misclassified (count)", fontsize=7)
for i,v in enumerate(cnts): axe.text(v+3, len(labs)-1-i, str(v), va="center", fontsize=6)
axe.set_title("Dominant confusions", fontsize=7, fontweight="bold", pad=3)
axe.tick_params(labelsize=6.3); axe.set_xlim(0,230)
panel_label(axe,"e",x=-0.30,y=1.16)

# ---- Panel f: delta accuracy per class sorted ----
axf = fig.add_subplot(gs[2, 4:6])
order=np.argsort([PER_CLASS[c][3] for c in CLASSES])
cls_o=[CLASSES[i] for i in order]; da_o=[PER_CLASS[c][3] for c in cls_o]
axf.barh(range(len(cls_o)), da_o, color=plt.cm.OrRd(np.array(da_o)/max(da_o)), edgecolor="black", linewidth=0.4)
axf.set_yticks(range(len(cls_o))); axf.set_yticklabels(cls_o, fontsize=6)
axf.set_xlabel("Δ Accuracy (pp)", fontsize=7)
for i,v in enumerate(da_o): axf.text(v+0.1,i,f"+{v}",va="center",fontsize=5.6)
axf.set_title("Per-class improvement", fontsize=7, fontweight="bold", pad=3)
axf.tick_params(labelsize=6.3); axf.set_xlim(0,10.5)
panel_label(axf,"f",x=-0.28,y=1.16)

fig.savefig("Fig3_performance.png", dpi=400, bbox_inches="tight")
fig.savefig("Fig3_performance.pdf", bbox_inches="tight")
print("saved Fig3_performance")
