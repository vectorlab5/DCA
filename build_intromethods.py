def F(name):
    return open(f'frag/{name}').read().rstrip()+"\n"

INTRO = r"""\section{Introduction}
\label{sec:introduction}

Deep learning has transformed histopathological image analysis, enabling
automated tissue classification, tumour grading, and biomarker
prediction~\cite{huang2024surface,kuntz2021gastrointestinal,chaunzwa2021deep,hirra2021breast,wetstein2022deep}.
Yet these models typically demand large annotated datasets to perform robustly,
a critical bottleneck in pathology where each sample must be labelled by an
expert. The problem is most acute for rare cancer subtypes and in
resource-limited settings, and it is compounded by the substantial variability of
histological images arising from tissue deformation, staining differences, and
scanner artefacts.

At the root of this challenge is the \textit{morphological heterogeneity} of
tissue. Unlike natural images, histological patches contain irregular structures
that vary dramatically across patients, preparation protocols, and scanning
conditions, so that the same tissue type can appear very different from slide to
slide. This forces models to allocate capacity to learning invariance to
nuisance geometric variation instead of diagnostic features, degrading both data
efficiency and cross-institution generalisation. Geometric normalisation---warping
irregular tissue into a standardised domain before feature extraction---has been
shown to help~\cite{huang2024surface}, but existing approaches require expensive
per-image optimisation, apply the same hand-crafted transformation to every
tissue type regardless of content, and decouple normalisation from classification
so the two cannot be jointly optimised. Stain-normalisation
methods~\cite{macenko2009method,shaban2019staingan} address colour, but not
geometric, variability and are therefore complementary.

We introduce \textbf{Deep Conformal Alignment (DCA)}, a framework that makes
geometric normalisation \textit{learnable} and integrates it directly into
end-to-end neural-network training. Building on spatial transformer
networks~\cite{jaderberg2015spatial} and diffeomorphic
registration~\cite{balakrishnan2019voxelmorph}, DCA parameterises deformations as
velocity fields integrated by scaling-and-squaring, guaranteeing
topology-preserving (diffeomorphic) transformations, and constrains them with a
differentiable \textit{conformal-energy} loss derived from the Cauchy--Riemann
equations so that learned warps preserve local angles---and thus local tissue
structure---while normalising global morphology. Because the transformation is
predicted in a single forward pass, DCA avoids the per-image optimisation of fixed
geometric methods and runs in real time. Methodological detail, including the
connection to quasiconformal mapping theory through the Beltrami coefficient, is
deferred to Methods so that the clinical results remain in the foreground.

Evaluating DCA on 100{,}000 colorectal-cancer patches across nine tissue classes,
we show that it (i) attains 93.2\% accuracy, outperforming spatial-transformer,
fixed-geometric, stain-normalisation, and self-supervised baselines with the same
backbone; (ii) is substantially more label-efficient, matching supervised
baselines that use several times more annotations; (iii) is complementary to
pathology foundation models, reaching 95.1\% accuracy when combined with a
pretrained encoder; (iv) generalises to an independent external cohort with the
smallest accuracy drop among compared methods; and (v) learns interpretable,
semantically adaptive transformations whose magnitude tracks tissue morphological
variability ($r=0.94$). Together these results indicate that domain-appropriate
geometric inductive bias is a practical route to data-efficient, robust
histopathology analysis.
"""

METHODS = r"""
%%=============================================================%%
%% METHODS  (CS theory relocated here)                         %%
%%=============================================================%%
\section{Methods}
\label{sec:method}

\subsection{Datasets}

We evaluate on two colorectal-cancer histopathology benchmarks.
\textit{NCT-CRC-HE-100K}~\cite{nct_dataset} contains 100{,}000 non-overlapping
$224\times224$ H\&E patches at 0.5\,$\mu$m/pixel across nine tissue classes
(ADI, BACK, DEB, LYM, MUC, MUS, NORM, STR, TUM). We use 5-fold cross-validation
with stratified splits (60\% train, 20\% validation, 20\% test per fold) and
report mean\,$\pm$\,s.d. across folds. \textit{CRC-VAL-HE-7K}~\cite{nct_dataset}
contains 7{,}180 patches from an independent cohort with different staining
protocols and scanners, used exclusively for cross-institution testing without
fine-tuning.

\subsection{Baselines and evaluation}

We compare DCA against 14 methods spanning standard CNNs (ResNet-18/50,
DenseNet-121, EfficientNet-B0), spatial-transformer methods (STN-Affine,
STN-TPS~\cite{jaderberg2015spatial}, Deformable
Convolution~\cite{dai2017deformable}), fixed geometric normalisation (CEM and
SEM~\cite{huang2024surface}), stain normalisation
(Macenko~\cite{macenko2009method}, StainGAN~\cite{shaban2019staingan}),
self-supervised pretraining (SimCLR~\cite{chen2020simple}), and pathology
foundation models (PLIP~\cite{huang2023plip}, UNI~\cite{chen2024uni},
CONCH~\cite{lu2024conch}) under both linear-probe and fine-tuned protocols. All
spatial-transformer and geometric methods use a ResNet-18 backbone for fair
comparison. We report top-1 accuracy, macro-F1, and Cohen's $\kappa$, and assess
significance with paired $t$-tests across folds with Bonferroni correction
($\dagger$: $p<0.05$; $\ddagger$: $p<0.01$).

\textbf{Implementation.} All models train for 50 epochs with AdamW
($\beta_1=0.9$, $\beta_2=0.999$, initial learning rate $10^{-3}$, weight decay
$10^{-4}$), cosine annealing with 5-epoch warmup, and batch size 32 on NVIDIA
A100 GPUs. Augmentation comprises random flips, rotation ($\pm15^\circ$), and
colour jitter ($\pm0.2$), disabled at validation and test. For DCA we set
$\lambda_{conf}=1.0$, $\lambda_{smooth}=0.1$, and $T=7$ (Table~\ref{tab:hyperparameter}).
Random seeds are fixed to \{42, 123, 456, 789, 1024\} for the five folds and
applied identically across methods. Foundation models use a $10\times$ lower
backbone learning rate for fine-tuning; SimCLR is pretrained for 200 epochs
(temperature 0.5) before supervised fine-tuning. Table~\ref{tab:comparison_prior}
summarises how DCA differs from prior geometric-transformation approaches.

""" + F('tab_comparison_prior.tex') + r"""

\subsection{Problem formulation}

Let $\Omega\subset\mathbb{R}^2$ denote the image domain and
$\mathcal{I}=L^2(\Omega,\mathbb{R}^3)$ the space of RGB images. Given a labelled
dataset $\mathcal{D}=\{(I_i,y_i)\}_{i=1}^N$ with $I_i\in\mathcal{I}$ and
$y_i\in\{1,\ldots,C\}$, we jointly learn a transformation network
$\mathcal{T}_\psi:\mathcal{I}\rightarrow\mathfrak{X}(\Omega)$ that maps each image
to a velocity field $v_i=\mathcal{T}_\psi(I_i)$ (in practice an $H\times W\times2$
tensor), from which a diffeomorphism $\phi_i=\exp(v_i)\in\text{Diff}^+(\Omega)$ is
obtained, and a classifier $f_\theta:\mathcal{I}\rightarrow\Delta^{C-1}$. The
transformed image is $\tilde{I}_i=I_i\circ\phi_i$ (backward warping via
differentiable bilinear interpolation). The learning problem is
\begin{equation}
\min_{\psi,\theta}\;\mathbb{E}_{(I,y)\sim\mathcal{D}}\left[\mathcal{L}_{cls}(f_\theta(\tilde{I}),y)+\lambda_{conf}\mathcal{E}_{conf}(\phi)+\lambda_{smooth}\mathcal{R}_{smooth}(v)\right],
\label{eq:objective}
\end{equation}
balancing classification accuracy, angle preservation, and deformation
smoothness.

\subsection{Diffeomorphic spatial transformer}

Rather than predicting $\phi$ directly, we predict a stationary velocity field
$v$ and obtain $\phi$ via the exponential map, $\phi=\exp(v)$
(Definition~\ref{def:exp_map}). The localisation network $g_\psi$ is a
U-Net~\cite{ronneberger2015unet} with four encoder blocks (channels
$[3,64,128,256,512]$) and a mirrored decoder with skip connections; the final
$1\times1$ convolution outputs the two velocity components and is initialised to
zero so that the transformation begins at identity. The exponential map is
approximated by scaling-and-squaring~\cite{arsigny2006logdiff}
(Algorithm~\ref{alg:scaling_squaring}), which guarantees a diffeomorphism for
bounded velocity magnitude (Proposition~\ref{prop:diffeomorphism}).

\begin{definition}[Exponential map]
\label{def:exp_map}
The exponential map $\exp:\mathfrak{X}(\Omega)\rightarrow\text{Diff}^+(\Omega)$ is
$\phi=\exp(v)=\lim_{T\rightarrow\infty}\left(\text{Id}+v/T\right)^T$, where
$\text{Id}$ is the identity transformation.
\end{definition}

""" + F('alg_scaling_squaring.tex') + r"""

\begin{proposition}[Diffeomorphism via scaling-and-squaring]
\label{prop:diffeomorphism}
Let $v:\Omega\rightarrow\mathbb{R}^2$ be a smooth stationary velocity field.
Algorithm~\ref{alg:scaling_squaring} produces $F(x)=x+\phi(x)$ approximating
$\exp(v)$ with error $O(2^{-T})$~\cite{arsigny2006logdiff}. If the scaled field
satisfies $\|v/2^T\|_{L^\infty}\leq\epsilon$ for sufficiently small $\epsilon$,
the result is a diffeomorphism, i.e.\ $\det(J_F(x))>0$ for all $x\in\Omega$.
\end{proposition}

In our experiments we verify empirically that $\min_x\det(J_F(x))>0.1$ across all
training and test samples and observe no folding artefacts.

\subsection{Conformal regularisation via differential geometry}

A smooth map is conformal if it preserves angles locally; in two dimensions this
is characterised by the Cauchy--Riemann equations (Definition~\ref{def:conformal}).
This property matters for histopathology because it maintains local structure
(nuclear spacing, glandular shape) while permitting normalisation of global
morphology.

\begin{definition}[Conformal map]
\label{def:conformal}
A smooth map $F:\Omega\rightarrow\Omega$ with Jacobian $J_F$ is conformal iff
$J_F$ is a scaled rotation at each point, equivalently iff it satisfies the
Cauchy--Riemann equations
$\partial F_1/\partial x=\partial F_2/\partial y$ and
$\partial F_1/\partial y=-\partial F_2/\partial x$.
\end{definition}

For $F(x)=x+\phi(x)$ we define the conformal energy as the $L^2$ deviation from
the Cauchy--Riemann equations,
\begin{equation}
\mathcal{E}_{conf}(\phi)=\frac{1}{|\Omega|}\int_\Omega\left[\left(\frac{\partial\phi_1}{\partial x}-\frac{\partial\phi_2}{\partial y}\right)^2+\left(\frac{\partial\phi_1}{\partial y}+\frac{\partial\phi_2}{\partial x}\right)^2\right]dx,
\label{eq:conformal_energy}
\end{equation}
discretised with central finite differences and replication padding. Strictly
conformal maps in 2D are highly restricted, so we appeal to \textit{quasiconformal}
mapping theory~\cite{ahlfors2006conformal}, which allows bounded angle distortion
measured by the Beltrami coefficient $\mu=\partial_{\bar z}F/\partial_z F$. A map
is conformal iff $\mu=0$, with maximal dilatation $K=(1+|\mu|)/(1-|\mu|)$
(Proposition~\ref{prop:beltrami}); minimising $\mathcal{E}_{conf}$ is equivalent
to minimising $\|\mu\|_{L^2}$, encouraging $K\approx1$. For typical learned
transformations we observe mean $|\mu|\approx0.15$ and $K\approx1.35$, i.e.\
quasiconformal maps with low distortion.

\begin{proposition}[Conformality and the Beltrami coefficient~\cite{ahlfors2006conformal}]
\label{prop:beltrami}
A smooth orientation-preserving map $F$ is conformal iff $\mu=0$ almost
everywhere. The maximal dilatation satisfies $K=(1+|\mu|)/(1-|\mu|)$, and
$\mathcal{E}_{conf}(\phi)=\frac{4}{|\Omega|}\int_\Omega|\mu|^2|\partial_zF|^2\,dx$
(see~\cite{lui2014brain}).
\end{proposition}

\subsection{End-to-end objective and training}

The full objective combines classification, conformal, and smoothness terms,
\begin{equation}
\mathcal{L}(\psi,\theta;I,y)=\mathcal{L}_{cls}(f_\theta(\tilde{I}),y)+\lambda_{conf}\mathcal{E}_{conf}(\phi)+\lambda_{smooth}\mathcal{R}_{smooth}(v),
\label{eq:full_loss}
\end{equation}
where $\mathcal{L}_{cls}$ is cross-entropy and
$\mathcal{R}_{smooth}(v)=\frac{1}{|\Omega|}\sum_{x}\|\nabla v(x)\|_F^2$ is a
total-variation regulariser on the velocity field, which favours piecewise-smooth
deformations while permitting sharp transitions at tissue boundaries. All
operations---scaling-and-squaring, bilinear warping, and conformal-energy
computation---are differentiable, enabling end-to-end optimisation by
backpropagation. The ResNet-18 classifier is initialised from ImageNet and the
U-Net final layer from zero, so training begins at the identity transformation.
Algorithm~\ref{alg:training} gives the complete procedure.

""" + F('alg_training.tex') + r"""

\textbf{Computational cost.} The per-image forward pass is dominated by the two
network passes, giving $O(HW(D_U+D_R))$ complexity---identical in order to
standard CNN classification. Scaling-and-squaring adds only $\sim$2\,ms to the
$\sim$15\,ms total inference on an A100 GPU. In contrast to fixed conformal
methods~\cite{huang2024surface} that require $O(n^3)$ per-image optimisation
(30--60\,s per image), DCA amortises the geometric cost during training
(Table~\ref{tab:computational}), enabling real-time deployment.

""" + F('tab_computational.tex')

open('body_intro.tex','w').write(INTRO)
open('body_methods.tex','w').write(METHODS)
print("intro chars:", len(INTRO), "methods chars:", len(METHODS))
