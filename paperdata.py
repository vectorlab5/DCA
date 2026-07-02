"""All quantitative values transcribed verbatim from paper_elsevier.tex tables.
These are the authors' real reported results (full A100 / 5-fold CV run held externally).
Every figure imports from here so nothing is fabricated at plot time."""

# --- Table 5: per-class accuracy + morphological variability (MV) ---
CLASSES = ["ADI","BACK","DEB","LYM","MUC","MUS","NORM","STR","TUM"]
CLASS_FULL = {"ADI":"Adipose","BACK":"Background","DEB":"Debris","LYM":"Lymphocytes",
              "MUC":"Mucus","MUS":"Smooth muscle","NORM":"Normal mucosa",
              "STR":"Cancer-assoc. stroma","TUM":"Tumour epithelium"}
PER_CLASS = {  # class: (ResNet, STN-TPS, DCA, delta, MV)
 "ADI":(94.8,95.6,96.9,2.1,0.31), "BACK":(98.9,99.1,99.4,0.5,0.18),
 "DEB":(83.2,87.1,90.5,7.3,0.72), "LYM":(80.1,84.5,87.8,7.7,0.68),
 "MUC":(86.4,89.0,92.1,5.7,0.54), "MUS":(92.4,93.5,94.8,2.4,0.35),
 "NORM":(89.2,91.3,93.2,4.0,0.42), "STR":(77.1,81.6,85.4,8.3,0.76),
 "TUM":(79.3,85.0,88.6,9.3,0.81)}
PER_CLASS_AVG = (87.4,90.8,93.2,5.8)
MV_DELTA_R = 0.94  # Pearson r, p<0.001

# --- Table 2: main comparison (mean, std) accuracy ---
MAIN_RESULTS = {  # method: (acc, std)  None std = not reported / not applicable
 "ResNet-18":(87.4,0.6),"ResNet-50":(88.5,0.5),"DenseNet-121":(88.1,0.6),
 "EfficientNet-B0":(88.9,0.5),"STN-Affine":(88.8,0.6),"STN-TPS":(90.8,0.5),
 "Deformable Conv":(89.5,0.4),"CEM+ResNet-18":(90.1,0.5),"SEM+ResNet-18":(89.4,0.6),
 "Macenko+ResNet-18":(88.2,0.5),"StainGAN+ResNet-18":(88.9,0.5),
 "SimCLR+FT":(89.8,0.5),"PLIP (linear)":(89.7,0.4),"PLIP (FT)":(92.1,0.4),
 "UNI (linear)":(91.2,0.4),"UNI (FT)":(94.3,0.3),"CONCH (linear)":(90.8,0.5),
 "CONCH (FT)":(93.7,0.3),"DCA (Ours)":(93.2,0.4),"DCA+Macenko":(93.8,0.4),
 "DCA+UNI":(95.1,0.3)}
# grouping for colouring
FOUNDATION = {"PLIP (linear)","PLIP (FT)","UNI (linear)","UNI (FT)","CONCH (linear)","CONCH (FT)","SimCLR+FT"}
DCA_METHODS = {"DCA (Ours)","DCA+Macenko","DCA+UNI"}

# --- Table 3: cross-dataset generalization (source, target, drop) ---
GENERALIZATION = {  # method: (source_acc, target_acc, drop)
 "ResNet-18":(87.4,82.6,-4.8),"STN-TPS":(90.8,87.6,-3.2),"CEM+ResNet-18":(90.1,87.2,-2.9),
 "UNI (FT)":(94.3,91.8,-2.5),"DCA (Ours)":(93.2,91.1,-2.1),"DCA+UNI":(95.1,93.4,-1.7)}

# --- Table 4: data efficiency (acc, std) at each fraction ---
FRACTIONS = [5,10,20,50,100]
DATA_EFF = {  # method: [(acc,std) per fraction]
 "ResNet-18":[(31.2,1.8),(43.5,1.5),(57.2,1.2),(73.8,0.9),(87.4,0.6)],
 "STN-TPS":[(38.7,1.6),(52.1,1.3),(64.8,1.0),(79.6,0.7),(90.8,0.5)],
 "CEM":[(36.4,1.7),(49.8,1.4),(62.5,1.1),(77.9,0.8),(90.1,0.5)],
 "SimCLR+FT":[(42.1,1.5),(56.3,1.2),(68.7,1.0),(80.2,0.7),(89.8,0.5)],
 "UNI (FT)":[(61.8,1.2),(74.2,0.9),(83.1,0.7),(89.7,0.5),(94.3,0.3)],
 "DCA":[(52.8,1.3),(66.4,1.0),(78.1,0.8),(87.5,0.5),(93.2,0.4)],
 "DCA+UNI":[(67.9,1.1),(79.8,0.8),(87.3,0.6),(92.1,0.4),(95.1,0.3)]}
DATA_EFF_RATIO = 4.2  # DCA at 10% matches standard at 42%

# --- Table 9: corruption robustness (acc, std) ---
ROBUST = {  # method: {cond:(acc,std)}
 "ResNet-18":{"Clean":(87.4,0.6),"Noise":(71.2,1.2),"Blur":(68.5,1.4),"JPEG":(75.8,1.0)},
 "STN-TPS":{"Clean":(90.8,0.5),"Noise":(76.4,1.0),"Blur":(73.1,1.2),"JPEG":(80.2,0.8)},
 "DCA":{"Clean":(93.2,0.4),"Noise":(82.1,0.8),"Blur":(79.8,1.0),"JPEG":(85.6,0.7)}}
CORRUPTIONS = ["Clean","Noise","Blur","JPEG"]

# --- Table 10: failure modes (count, pct) ---
FAILURES = [("STR↔TUM confusion",198,29.1),("DEB↔MUC confusion",142,20.9),
            ("LYM↔STR confusion",108,15.9),("Over-aggressive deformation",87,12.8),
            ("Boundary/ambiguous",145,21.3)]
N_MISCLASS = 680

# --- Table 6: ablation (key rows) ---
ABLATION = {  # label: (acc, dAcc)
 "Full DCA":(93.2,0.0),"w/o conformal loss":(89.8,-3.4),"w/o smoothness":(91.5,-1.7),
 "Direct displ. (no SS)":(88.2,-5.0),"STN-TPS (no geom.)":(90.8,-2.4),
 "VoxelMorph-style":(91.4,-1.8),"Frozen backbone":(89.1,-4.1),"Two-stage":(90.8,-2.4)}

# --- Table 7: hyperparameter grid (rows=lambda_conf, cols=lambda_smooth) ---
HP_LCONF = [0.1,0.5,1.0,2.0,5.0]
HP_LSMOOTH = [0.01,0.05,0.1,0.2,0.5]
HP_GRID = [[88.4,88.9,89.2,89.0,88.1],
           [91.2,91.8,92.1,91.7,90.5],
           [92.1,92.8,93.2,92.6,91.2],
           [91.5,92.3,92.7,92.1,90.8],
           [89.8,90.4,90.9,90.2,89.1]]

# --- Per-tissue deformation stats (Results text, line 624) ---
DEFORM = {  # class: (mean_displacement_px, mean_conformal_energy)
 "TUM":(18.2,0.087),"NORM":(9.4,0.042),"MUS":(5.1,0.021)}
DEFORM_DELTA_R = 0.91  # Pearson r between mean||phi|| and delta-accuracy
CONF_ENERGY_BLUE_FRAC = 92  # % of pixels with E_conf < 0.10

# --- Headline numbers ---
HEADLINE = {"acc":93.2,"uni_ft":94.3,"dca_uni":95.1,"n_train":100000,
            "n_classes":9,"data_eff":4.2,"infer_ms":15,"cem_ms":"30-60 s"}

if __name__=="__main__":
    print("paperdata OK:", len(MAIN_RESULTS),"methods,",len(PER_CLASS),"classes")
