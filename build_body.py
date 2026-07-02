# Assembles the results-forward npj body from newly-written prose + verbatim fragments.
def F(name):
    return open(f'frag/{name}').read().rstrip()+"\n"

RESULTS = r"""
%%=============================================================%%
%% RESULTS  (results-forward npj structure)                    %%
%%=============================================================%%
\section{Results}
\label{sec:results}

\subsection{A geometry-aware framework for label-efficient tissue classification}

We studied colorectal cancer histopathology, where nine tissue classes must be
distinguished from haematoxylin-and-eosin (H\&E) stained image patches
(Fig.~\ref{fig:overview}a): adipose (ADI), background (BACK), debris (DEB),
lymphocytes (LYM), mucus (MUC), smooth muscle (MUS), normal colon mucosa
(NORM), cancer-associated stroma (STR), and colorectal adenocarcinoma
epithelium (TUM). A central obstacle to automated diagnosis in this setting is
\textit{morphological heterogeneity}: the same tissue class can appear markedly
different across patients, preparation protocols, and scanners, so that models
must expend capacity learning invariance to nuisance geometric variation rather
than diagnostic features. We quantified this heterogeneity per class as the
intra-class morphological variability (MV), the mean pairwise distance of
deep features within a class (Fig.~\ref{fig:overview}b,e). MV spans a wide range,
from highly regular background and adipose tissue (MV~$=0.18$ and $0.31$) to
structurally irregular tumour and stroma (MV~$=0.81$ and $0.76$).

Deep Conformal Alignment (DCA) addresses this variability by learning to
normalise tissue geometry before classification (Fig.~\ref{fig:overview}c).
Each input patch is passed through a localisation network that predicts a
smooth velocity field; this field is integrated into a topology-preserving
(diffeomorphic) deformation that warps the patch into a canonical form, which is
then classified by a standard convolutional backbone. The entire pipeline is
trained end-to-end, and a differentiable conformal-energy penalty encourages the
learned deformation to preserve local angles---maintaining the relative
arrangement of nuclei and glandular structures---while normalising global shape
(Fig.~\ref{fig:overview}d). Unlike fixed geometric-normalisation methods that
solve a separate optimisation for every slide, DCA amortises this cost during
training and applies the transformation in a single forward pass
($\sim$15\,ms per patch). Full architectural and mathematical detail is given in
Methods.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Fig1_overview.pdf}
\caption{\textbf{Study overview and the morphological-heterogeneity challenge in
colorectal histopathology.} (a) Representative H\&E tiles for the nine tissue
classes. (b) Intra-class appearance variation is large for irregular tissue
(tumour, TUM) and small for regular tissue (background, BACK). (c) The DCA
pipeline: a U-Net localisation network predicts a velocity field that is
integrated by scaling-and-squaring into a diffeomorphic deformation; the warped,
canonicalised patch is classified by a ResNet-18 backbone; training combines a
classification loss with conformal-energy and smoothness regularisers.
(d) Conformal normalisation applied to a real tissue patch, with the associated
angle-distortion (conformal-energy) map. (e) Per-class morphological variability
(MV), ordered from most to least heterogeneous. (f) Study design: 100{,}000
training patches (NCT-CRC-HE-100K, 5-fold cross-validation) and an independent
7{,}180-patch external cohort (CRC-VAL-HE-7K) held out for cross-institution
testing.}
\label{fig:overview}
\end{figure*}

\subsection{Learned transformations adapt to tissue morphology}

A defining property of DCA is that the normalisation it applies is not fixed but
adapts to the semantic content of each patch. Figure~\ref{fig:normalization}
shows learned deformation fields and the resulting canonicalised tissue for three
representative classes. For tumour epithelium, which is morphologically the most
irregular, DCA applies the largest deformations (mean displacement
$\bar{\|\phi\|}=18.2$\,px, mean conformal energy
$\bar{\mathcal{E}}_{conf}=0.087$), warping irregular tumour boundaries and
heterogeneous cell distributions toward a canonical layout. For normal mucosa the
transformation is more restrained ($\bar{\|\phi\|}=9.4$\,px,
$\bar{\mathcal{E}}_{conf}=0.042$), primarily aligning glandular structures, and
for smooth muscle---already regular and aligned---the deformation is minimal
($\bar{\|\phi\|}=5.1$\,px, $\bar{\mathcal{E}}_{conf}=0.021$).

Two observations confirm that these transformations are both adaptive and
geometrically well-behaved. First, the magnitude of deformation a class receives
scales with its morphological variability and, in turn, with the accuracy gain
DCA delivers for that class (Fig.~\ref{fig:normalization}f; Pearson $r=0.91$
between mean displacement and per-class improvement). Second, the conformal-energy
maps are dominated by low values: across all classes, 92\% of pixels satisfy
$\mathcal{E}_{conf}<0.10$ (Fig.~\ref{fig:normalization}g), indicating that the
learned maps are approximately angle-preserving (quasiconformal with low
distortion) despite the large differences in deformation magnitude. This semantic
adaptivity---aggressive normalisation for irregular tissue, gentle adjustment for
structured tissue---emerges automatically from end-to-end optimisation and is not
imposed by hand.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Fig2_normalization.pdf}
\caption{\textbf{DCA learns semantically adaptive, angle-preserving
normalisation on real tissue.} (a--c) For tumour (TUM), normal mucosa (NORM), and
smooth muscle (MUS): original H\&E patch, learned deformation field $\varphi$,
normalised tissue, and conformal-energy map (blue, near-conformal; red, high
angle distortion). Per-tissue mean displacement and mean conformal energy are
annotated. (d,e) Mean displacement and mean conformal energy increase with tissue
irregularity (TUM $>$ NORM $>$ MUS). (f) Deformation magnitude correlates with
the per-class accuracy gain ($r=0.91$). (g) Across all tissue, 92\% of pixels
have conformal energy below 0.10, confirming quasiconformal (angle-preserving)
behaviour.}
\label{fig:normalization}
\end{figure*}

\subsection{DCA improves classification across nine tissue types}

On the 100{,}000-patch NCT-CRC-HE-100K benchmark with 5-fold cross-validation,
DCA reaches 93.2\% accuracy and 92.4\% macro-F1 (Table~\ref{tab:main_results}).
This exceeds every geometry-agnostic and geometry-fixed baseline trained with the
same ResNet-18 backbone: DCA improves on the strongest standard CNN
(EfficientNet-B0) by 4.3 percentage points (pp), on the best spatial-transformer
method (STN-TPS) by 2.4\,pp, on fixed conformal normalisation (CEM) by 3.1\,pp,
and on generative stain normalisation (StainGAN) by 4.3\,pp
(Fig.~\ref{fig:performance}a). All differences are statistically significant
($p<0.01$, paired $t$-test with Bonferroni correction).

The per-class analysis reveals where and why DCA helps
(Fig.~\ref{fig:performance}b,d,f; Table~\ref{tab:per_class}). The accuracy gain
over ResNet-18 is largest for the most morphologically variable tissues---tumour
($+9.3$\,pp), stroma ($+8.3$\,pp), and debris ($+7.3$\,pp)---and smallest for the
most regular tissues (background $+0.5$\,pp, adipose $+2.1$\,pp). Across classes,
the improvement correlates strongly with morphological variability (Pearson
$r=0.94$, $p<0.001$; Fig.~\ref{fig:performance}d), directly linking DCA's benefit
to the heterogeneity it is designed to normalise. Consistently, the confusion
matrix (Fig.~\ref{fig:performance}c) shows the largest reductions in
error precisely among morphologically similar class pairs: STR$\rightarrow$TUM
confusion falls from 12.3\% to 5.8\%, DEB$\rightarrow$MUC from 8.7\% to 3.2\%, and
LYM$\rightarrow$STR from 9.1\% to 4.5\% (Fig.~\ref{fig:performance}e).

DCA is also complementary to large-scale pretraining. A fine-tuned pathology
foundation model (UNI) attains the highest single-method accuracy (94.3\%),
1.1\,pp above DCA, as expected given its access to millions of pretraining
images. However, replacing DCA's ResNet-18 backbone with UNI's pretrained encoder
while retaining DCA's geometric-normalisation head raises accuracy to 95.1\%,
surpassing both DCA and fine-tuned UNI alone ($p<0.05$) with no additional
labelled data---evidence that geometric normalisation contributes benefits
orthogonal to those of foundation-model pretraining. Combining DCA with Macenko
stain normalisation likewise gives a further $+0.6$\,pp, confirming that
geometric and colour normalisation address distinct sources of variability.

""" + F('tab_main_results.tex') + F('tab_per_class.tex') + r"""

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Fig3_performance.pdf}
\caption{\textbf{Classification performance across methods and tissue classes.}
(a) Accuracy on NCT-CRC-HE-100K for 21 methods (mean $\pm$ s.d. over 5 folds);
DCA (vermillion) outperforms all backbone-matched baselines and is complemented
by, rather than competing with, foundation models (blue). (b) Per-class accuracy
for ResNet-18, STN-TPS, and DCA. (c) Confusion matrices before (ResNet-18) and
after (DCA) geometric normalisation. (d) Per-class accuracy gain versus
morphological variability ($r=0.94$). (e) Largest reductions in inter-class
confusion. (f) Per-class improvement of DCA over ResNet-18, ordered by
magnitude.}
\label{fig:performance}
\end{figure*}

\subsection{Label efficiency and cross-institution generalisation}

Because expert annotation is the principal bottleneck in computational pathology,
we assessed how DCA performs when labelled data are scarce
(Table~\ref{tab:data_efficiency}; Fig.~\ref{fig:efficiency}a). Trained on only
10\% of the labelled data (6{,}000 patches), DCA reaches 66.4\% accuracy,
exceeding ResNet-18 at the same budget by 22.9\,pp and approaching ResNet-18's
performance at roughly three-to-four times more labelled data
(Fig.~\ref{fig:efficiency}b): interpolating the plotted ResNet-18 curve, it
attains DCA's 10\%-data accuracy only at $\sim$33\% of the labels. The advantage
is largest in the most label-scarce regime---at 5\% data, DCA leads ResNet-18 by
21.6\,pp---and the gap narrows smoothly as data increase. DCA at 10\% also
outperforms self-supervised SimCLR pretraining at 10\% (56.3\%) by 10.1\,pp,
indicating that an explicit geometric inductive bias yields greater label
efficiency than unsupervised representation learning alone in this domain.
Combining DCA with a foundation-model encoder pushes 10\%-data accuracy to 79.8\%,
above UNI alone (74.2\%), so the two forms of prior compound
(Fig.~\ref{fig:efficiency}f).

Robust transfer across institutions is equally important for clinical
deployment. Trained on NCT-CRC-HE-100K and tested without fine-tuning on the
independent CRC-VAL-HE-7K cohort---acquired with different scanners, staining
batches, and preparation protocols---DCA loses only 2.1\,pp of accuracy, versus
4.8\,pp for ResNet-18 and 3.2\,pp for STN-TPS (Table~\ref{tab:generalization};
Fig.~\ref{fig:efficiency}c,d). DCA combined with a foundation-model encoder shows
the smallest drop of all (1.7\,pp). The external tiles in
Fig.~\ref{fig:efficiency}e illustrate the visual domain shift the model
withstands. This improved generalisation is consistent with DCA normalising
scanner- and protocol-specific geometric variation while its diffeomorphic
constraint discourages source-specific overfitting.

""" + F('tab_data_efficiency.tex') + F('tab_generalization.tex') + r"""

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Fig4_efficiency.pdf}
\caption{\textbf{Label efficiency and cross-institution generalisation.}
(a) Learning curves across labelled-data fractions (5--100\%); DCA (vermillion)
leads supervised baselines throughout, with the largest margin in low-data
regimes. (b) DCA reaches 66.4\% accuracy using 10\% of labels; the plotted
ResNet-18 curve attains the same accuracy only near 33\% of labels (grey marker).
(c) Source (100K) versus external (7K) accuracy for six methods. (d) Accuracy
drop under domain shift (smaller is better); DCA and DCA+encoder are most robust.
(e) Representative unseen tiles from the external CRC-VAL-HE-7K cohort.
(f) Summary: DCA delivers substantially higher accuracy per labelled example
(reported peak label-efficiency up to 4.2$\times$).}
\label{fig:efficiency}
\end{figure*}

\subsection{Robustness, component contributions, and interpretable failures}

Finally, we examined DCA's robustness, the contribution of its components, and
its characteristic errors (Fig.~\ref{fig:robustness}). Under three image
corruptions applied at test time---Gaussian noise, blur, and aggressive JPEG
compression---DCA retains higher accuracy than ResNet-18 and STN-TPS in every
condition, and its relative advantage widens under degradation
(Fig.~\ref{fig:robustness}a; Table~\ref{tab:robustness}): the margin over
ResNet-18 grows from 5.8\,pp on clean data to 10.9\,pp under noise and 11.3\,pp
under blur. Defining transformations on spatial structure rather than pixel
intensity, and constraining them to be smooth and angle-preserving, plausibly
provides implicit regularisation against such artefacts.

Ablating DCA's components confirms that the geometric constraints drive its
performance (Fig.~\ref{fig:robustness}b; Table~\ref{tab:ablation}). Removing the
conformal-energy loss costs 3.4\,pp---the single largest drop among the loss
terms---while replacing the diffeomorphic velocity parameterisation with a direct
displacement field costs 5.0\,pp, confirming that both angle preservation and
topology preservation are necessary. The method is robust to its two key
regularisation weights, maintaining $>$91\% accuracy across a broad plateau of
$\lambda_{conf}$ and $\lambda_{smooth}$ values, with the optimum at
$\lambda_{conf}=1.0$, $\lambda_{smooth}=0.1$ (Fig.~\ref{fig:robustness}c;
Table~\ref{tab:hyperparameter}).

Examining the errors DCA does make (Fig.~\ref{fig:robustness}d;
Table~\ref{tab:failure}) shows they are concentrated in genuinely ambiguous
cases: confusions between morphologically overlapping classes that co-occur in
the tumour microenvironment (STR$\leftrightarrow$TUM, 29.1\% of errors;
DEB$\leftrightarrow$MUC, 20.9\%; LYM$\leftrightarrow$STR, 15.9\%) and
boundary/ambiguous patches (21.3\%). A minority of errors (12.8\%) arise from
over-aggressive deformation and are associated with elevated conformal energy.
Indeed, misclassified patches carry significantly higher mean conformal energy
than correct ones (0.089 versus 0.042, $p<0.001$), suggesting that conformal
energy could serve as an intrinsic uncertainty signal
(Fig.~\ref{fig:robustness}e).

""" + F('tab_robustness.tex') + F('tab_ablation.tex') + F('tab_hyperparameter.tex') + F('tab_failure.tex') + r"""

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Fig5_robustness.pdf}
\caption{\textbf{Robustness, component ablation, and interpretable failure
modes.} (a) Accuracy under clean and corrupted inputs (noise, blur, JPEG); DCA's
margin widens under corruption. (b) Ablation: change in accuracy relative to full
DCA when each component is removed or replaced (conformal loss and diffeomorphic
parameterisation contribute most). (c) Hyperparameter sensitivity over
$\lambda_{conf}\times\lambda_{smooth}$, with a broad high-accuracy plateau and the
optimum boxed. (d) Distribution of the 680 misclassified test patches by failure
mode. (e) Representative failure cases (real DCA outputs): original patch, learned
deformation, transformed tissue, and conformal-energy map.}
\label{fig:robustness}
\end{figure*}
"""

DISCUSSION = r"""
%%=============================================================%%
%% DISCUSSION                                                  %%
%%=============================================================%%
\section{Discussion}
\label{sec:discussion}

Deep Conformal Alignment shows that morphological variability in histopathology,
a principal driver of poor data efficiency and limited cross-institution
transfer, can be addressed by learning to normalise tissue geometry as part of
the classification pipeline rather than as a fixed preprocessing step. Three
findings are of practical significance. First, the accuracy DCA gains for a given
tissue class scales with that class's morphological heterogeneity
($r=0.94$), so the method concentrates its benefit exactly where irregularity is
greatest---tumour, stroma, and debris---and reduces confusion between
morphologically overlapping classes. Second, DCA is markedly label-efficient,
matching supervised baselines that use roughly three-to-four times more
annotations and outperforming self-supervised pretraining in the low-data regime;
this matters most where expert labels are scarce, such as rare subtypes and
resource-limited settings. Third, geometric normalisation is complementary to
foundation-model pretraining: adding DCA's normalisation head to a pretrained
encoder improves both accuracy and cross-institution robustness beyond either
component alone, so the approach remains useful in the foundation-model era rather
than being superseded by it.

The learned transformations are also interpretable. Their magnitude adapts to
tissue type, they remain approximately angle-preserving (92\% of pixels below a
low conformal-energy threshold), and the residual conformal energy is elevated
precisely on the patches the model misclassifies, pointing to conformal energy as
a candidate intrinsic uncertainty measure for clinical decision support.

Several limitations define the scope of these conclusions and motivate future
work. Both datasets are colorectal cancer with H\&E staining; generalisation to
other organs (breast, lung, brain) and to other modalities (immunohistochemistry,
fluorescence) remains to be established, although the underlying geometric
principles are not tissue-specific. Extension to gigapixel whole-slide analysis
would require hierarchical architectures that maintain geometric coherence across
scales. Establishing a calibrated relationship between conformal energy and
predictive confidence could turn the interpretability signal observed here into a
usable uncertainty estimate. Finally, integrating geometric normalisation with
multimodal foundation models that combine image, text, and molecular data is a
natural next step toward more comprehensive diagnostic systems. Overall, DCA
indicates that building domain-appropriate geometric structure into deep learning
is a productive route to more label-efficient, robust, and interpretable clinical
image analysis.
"""

open('body_results.tex','w').write(RESULTS)
open('body_discussion.tex','w').write(DISCUSSION)
print("results chars:", len(RESULTS), "discussion chars:", len(DISCUSSION))
