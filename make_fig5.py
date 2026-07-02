import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import numpy as np
from figtools import panel_label, CB, imshow_tile
from paperdata import (ROBUST, CORRUPTIONS, ABLATION, HP_LCONF, HP_LSMOOTH, HP_GRID,
                       FAILURES, N_MISCLASS)

fig = plt.figure(figsize=(7.2, 8.8))
gs = GridSpec(3, 6, figure=fig, height_ratios=[1.15,1.15,1.35], hspace=0.55, wspace=1.1,
              left=0.10, right=0.96, top=0.94, bottom=0.05)

# ---- Panel a: corruption robustness grouped bars ----
axa=fig.add_subplot(gs[0,0:3])
methods=["ResNet-18","STN-TPS","DCA"]; x=np.arange(len(CORRUPTIONS)); w=0.26
mc={"ResNet-18":CB["grey"],"STN-TPS":CB["skyblue"],"DCA":CB["vermillion"]}
for i,m in enumerate(methods):
    accs=[ROBUST[m][c][0] for c in CORRUPTIONS]
    errs=[ROBUST[m][c][1] for c in CORRUPTIONS]
    axa.bar(x+(i-1)*w, accs, w, yerr=errs, capsize=1.5, label=m, color=mc[m],
            edgecolor="black", linewidth=0.4, error_kw=dict(lw=0.5))
axa.set_xticks(x); axa.set_xticklabels(CORRUPTIONS, fontsize=6.8)
axa.set_ylabel("Accuracy (%)", fontsize=7.5); axa.set_ylim(60,99)
axa.legend(fontsize=5.6, loc="upper center", ncol=3, frameon=False, columnspacing=0.8, handletextpad=0.4, bbox_to_anchor=(0.5,0.99))
axa.tick_params(labelsize=6.5)
axa.set_title("Robustness to image corruptions", fontsize=7.8, fontweight="bold", pad=4)
panel_label(axa,"a",x=-0.14,y=1.05)

# ---- Panel b: ablation (delta accuracy) ----
axb=fig.add_subplot(gs[0,3:6])
labs=[k for k in ABLATION if k!="Full DCA"]
dvals=[ABLATION[k][1] for k in labs]
order=np.argsort(dvals)  # most negative first (bottom)
labs_o=[labs[i] for i in order]; dv_o=[dvals[i] for i in order]
axb.barh(range(len(labs_o)), dv_o, color=CB["vermillion"], edgecolor="black", linewidth=0.4)
axb.set_yticks(range(len(labs_o))); axb.set_yticklabels(labs_o, fontsize=5.8)
axb.set_xlabel("Δ Accuracy vs full DCA (pp)", fontsize=7)
for i,v in enumerate(dv_o): axb.text(v-0.05,i,f"{v}",va="center",ha="right",fontsize=5.6)
axb.axvline(0,color="black",lw=0.6)
axb.tick_params(labelsize=6.3); axb.set_xlim(-6,0.5)
axb.set_title("Ablation of components", fontsize=7.6, fontweight="bold", pad=4)
panel_label(axb,"b",x=-0.42,y=1.05)

# ---- Panel c: hyperparameter heatmap ----
axc=fig.add_subplot(gs[1,0:3])
grid=np.array(HP_GRID)
im=axc.imshow(grid, cmap="viridis", aspect="auto")
axc.set_xticks(range(len(HP_LSMOOTH))); axc.set_xticklabels(HP_LSMOOTH, fontsize=6.3)
axc.set_yticks(range(len(HP_LCONF))); axc.set_yticklabels(HP_LCONF, fontsize=6.3)
axc.set_xlabel(r"$\lambda_{smooth}$", fontsize=8); axc.set_ylabel(r"$\lambda_{conf}$", fontsize=8)
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        axc.text(j,i,f"{grid[i,j]:.1f}", ha="center", va="center", fontsize=5.6,
                 color="white" if grid[i,j]<91.5 else "black")
# mark optimum
oi,oj=np.unravel_index(np.argmax(grid),grid.shape)
axc.add_patch(plt.Rectangle((oj-0.5,oi-0.5),1,1,fill=False,edgecolor=CB["vermillion"],lw=1.8))
# compact vertical colourbar on panel c's right; panel d carries no left-side labels
cb=fig.colorbar(im,ax=axc,fraction=0.045,pad=0.03); cb.set_label("Acc. (%)",fontsize=6)
cb.ax.tick_params(labelsize=5.6)
axc.set_title("Hyperparameter sensitivity", fontsize=7.6, fontweight="bold", pad=4)
panel_label(axc,"c",x=-0.16,y=1.06)

# ---- Panel d: failure-mode distribution ----
axd=fig.add_subplot(gs[1,3:6])
flabs=[f[0].replace(" confusion","").replace("Over-aggressive ","Over-agg. ") for f in FAILURES]
fpct=[f[2] for f in FAILURES]
colors_f=plt.cm.OrRd(np.linspace(0.4,0.85,len(flabs)))
order=np.argsort(fpct)
fl_o=[flabs[i] for i in order]; fp_o=[fpct[i] for i in order]
axd.barh(range(len(fl_o)), fp_o, color=colors_f, edgecolor="black", linewidth=0.4)
axd.set_yticks([])
# category name inside/near bar base, percentage at bar tip
for i,(lab,v) in enumerate(zip(fl_o,fp_o)):
    axd.text(0.4, i, lab, va="center", ha="left", fontsize=5.8,
             color="white" if v>18 else "black")
    axd.text(v+0.4, i, f"{v}%", va="center", fontsize=5.8)
axd.set_xlabel("Share of errors (%)", fontsize=7)
axd.set_xlim(0,34)
axd.tick_params(labelsize=6.3)
axd.set_title(f"Failure-mode analysis (n={N_MISCLASS})", fontsize=7.2, fontweight="bold", pad=4)
panel_label(axd,"d",x=-0.06,y=1.05)

# ---- Panel e: interpretability / failure images (real) ----
fc = mpimg.imread("failure_cases.png")
FR={"r2":(701,1193),"r3":(1313,1804)}
FCOLS={"Original":(30,522),"Grid":(638,1113),"Transformed":(1212,1704),"Energy":(1803,2295)}
CT={"Original":"Original H&E","Grid":"Deformation φ","Transformed":"Transformed","Energy":"Conformal energy"}
ge=gs[2,0:6].subgridspec(2,4,hspace=0.10,wspace=0.06)
rows=[("r2",0),("r3",1)]
rowlab=["Over-aggressive\ndeformation (TUM)","Boundary/ambiguous\ncase"]
for ri,(rk,rr) in enumerate(rows):
    r0,r1=FR[rk]
    for ci,col in enumerate(FCOLS):
        c0,c1=FCOLS[col]
        ax=fig.add_subplot(ge[rr,ci]); imshow_tile(ax, fc[r0:r1,c0:c1])
        if rr==0: ax.set_title(CT[col], fontsize=6.6, fontweight="bold", pad=2)
        if ci==0:
            ax.set_ylabel(rowlab[ri], fontsize=5.8, rotation=0, ha="right", va="center", labelpad=6)
            if ri==0: panel_label(ax,"e",x=-0.52,y=1.20)
fig.text(0.10, 0.335, "Interpretability & characteristic failure cases (real DCA outputs)",
         fontsize=7.6, fontweight="bold", ha="left")

fig.savefig("Fig5_robustness.png", dpi=400, bbox_inches="tight")
fig.savefig("Fig5_robustness.pdf", bbox_inches="tight")
print("saved Fig5_robustness")
