# ARG-PASS v2.0

**Antibiotic Resistance Gene prediction by PAirwise Sequence vs Structure**

Structure-based functional prediction of antibiotic resistance genes. ARG-PASS aligns
candidate protein structures against conserved regions of antibiotic resistance protein
(ARP) structures using Foldseek, then predicts function with a one-class SVM trained on the
sequence identity versus TM-score distribution of each ARG class.

> **This branch is ARG-PASS v2.0, not yet published.**
> For the version accompanying the Microbiome paper, see the [`v1.0` tag](../../tree/v1.0)
> or [`README_v1.0.md`](README_v1.0.md). v2.0 supersedes it and is described in
> [reference not yet available].

---

## Two modes

Both modes share the same architecture: ARP structures are clustered at 20% sequence
identity, conserved residues are identified within each cluster, and all candidate structures
are assigned to these cluster-level models. The modes differ only in how conserved
residues are identified.

| Mode | Flag | Conserved residues identified by | Use when |
|---|---|---|---|
| **v2.0** (default) | `--mode v2.0` | CONSTRUCT — evolutionary rates weighted by spatially proximate neighbours | Precision matters, particularly for antibiotic resistance genes at clinically relevant MICs |
| **lddt** (relaxed) | `--mode lddt` | lDDT-based structural conservation, as in the original ARG-PASS framework | Sensitivity matters, and to also detect ARG-like folds conferring pre-resistance MICs |

---

## ARG classes

Each ARG class is represented by one or more structural models, built from ARP
structures clustered at 20% sequence identity. Pass a model name to `--class`, or use
`--class all` (the default) to test a candidate against every model available in the
selected mode.

Most models are common to both modes. Where a model exists in only one mode, this is
noted in the last column.

| `--class` argument | ARG class | Resistance to | Available in |
|---|---|---|---|
| `AAC_1` | AAC(2') | aminoglycosides | both |
| `AAC_2` | AAC(3) | aminoglycosides | both |
| `AAC_3` | AAC(3) | aminoglycosides | both |
| `AAC_4` | AAC(6') | aminoglycosides | both |
| `AAC_5` | AAC(6') | aminoglycosides | both |
| `AAC_6` | AAC(6') | aminoglycosides | both |
| `ANT_1` | ANT(3''); ANT(9) | aminoglycosides | both |
| `ANT_2` | ANT(6) | streptomycin | both |
| `APH_1` | APH(2'') | aminoglycosides | both |
| `APH_2` | APH(3') | aminoglycosides | both |
| `APH_3` | APH(6) | aminoglycosides | both |
| `APH_4` | APH(9) | aminoglycosides | `lddt` only |
| `class_A_1` | class A β-lactamases | β-lactams | both |
| `class_A_2` | class A β-lactamases | β-lactams | both |
| `sub_class_B1` | class B1 β-lactamases | β-lactams | `v2.0` only |
| `sub_class_B2` | class B2 β-lactamases | β-lactams | `v2.0` only |
| `sub_class_B1_B2` | class B1 and B2 β-lactamases | β-lactams | `lddt` only |
| `sub_class_B3` | class B3 β-lactamases | β-lactams | both |
| `class_C` | class C β-lactamases | β-lactams | both |
| `class_D_1` | class D β-lactamases | β-lactams | both |
| `class_D_2` | class D β-lactamases | β-lactams | both |
| `DFR` | dihydrofolate reductases | trimethoprim | both |
| `PBP_1` | Penicillin Binding Proteins 1 | β-lactams | `lddt` only |
| `PBP_2` | Penicillin Binding Proteins 2 and 3| β-lactams | `lddt` only |
| `SUL` | mobile dihydroperoate synthetases | sulfonamides | both |
| `TRPP` | Tetracycline-resistant Ribosomal Protection Proteins | tetracycline | both |

### Differences between modes

The two modes derive their models independently, so the model sets are not identical.

**class B β-lactamases.** The v2.0 mode resolves subclasses B1 and B2 as separate
models; the lDDT mode uses a single combined `sub_class_B1_B2` model.

**APH_4.** the 20% sequence identity cluster contained
fewer than four structures, so they are omitted from the v2.0 mode.

**Penicillin-binding proteins** omitted from v2.0 as PBPs rely on point mutations which can mislead conserved residue detection using CONSTRUCT

## Input

Protein structures as `.pdb` files (computational or experimental). Place them in a single directory.

ARG-PASS does not predict structures. To screen protein *sequences*, which requires
a pre-screening and computational structure prediction by ColabFold, use the ARG-PASS webserver
[URL to be inserted].

---

## Installation

```bash
git clone https://github.com/btroppo/ARG-PASS.git
cd ARG-PASS
git checkout v2.0-dev

conda env create -f environment.yml
conda activate argpass
```

The conserved-region ARP structure Foldseek databases (~30 MB) are included in the repository.

---

## Usage

Run all ARG classes in the default mode:

```bash
python3 -m argpass.cli --input structures/ --out results/predictions.csv
```

Run a single ARG class:

```bash
python3 -m argpass.cli --input structures/ --class sub_class_B1 --out results/predictions.csv
```

Run the relaxed mode:

```bash
python3 -m argpass.cli --input structures/ --mode lddt --out results/predictions.csv
```

### Options

| Option | Default | Description |
|---|---|---|
| `--input` | required | Directory containing candidate `.pdb` structures |
| `--out` | required | Path of the output CSV; figures and alignments are written alongside it |
| `--mode` | `v2.0` | `v2.0` or `lddt` |
| `--class` | `all` | ARG class to test, or `all` for every available class |
| `--databases` | `databases` | Root of the Foldseek databases directory |
| `--foldseek-bin` | auto | Path to the Foldseek executable, if not on `PATH` |
| `--threads` | auto | Threads passed to Foldseek |
| `--no-plots` | off | Skip figure generation |
| `--no-exhaustive` | off | Disable `--exhaustive-search` (faster, results may differ) |

---

## Try the example

one structure is included:

```bash
python3 -m argpass.cli --input example/ --class sub_class_B1 --out example/output/prediction.csv
```

---

## Output

A CSV with one row per candidate per ARG class:

| Column | Description |
|---|---|
| `candidate` | Candidate structure name |
| `ARG_class` | ARG class model tested against |
| `mode` | `v2.0` or `lddt` |
| `prediction` | `yes` or `no` |
| `decision_value` | Signed distance from the one-class SVM boundary; higher is more confident and a negative value is outside the boundary and predicted non-functional|
| `best_subject_tmscore` | Closest conserved ARP region by TM-score |
| `TM-score` | TM-score of that alignment |
| `seqID` | Sequence identity of corresponding alignment |
| `candidate_coverage` | Target length relative to candidate length |
| `n_alignments` | Alignments returned for this candidate |
| `n_training_points` | Points in the class training distribution |
| `coverage_filter_applied` | Whether the coverage filter was applied to the training set |

Alongside the CSV, for each class:

- `{class}_alignments.out` — raw Foldseek output
- `{class}_seqID_vs_TM-score.png` — candidates over the training distribution
- `{class}_SVM_boundary.png` — candidates in scaled feature space with the decision boundary

---

## Repository layout

```
ARG-PASS/
├── argpass/            # package
├── databases/
│   ├── v2.0/{class}/   # default mode conserved ARP region databases + training distribution
│   └── lddt/{class}/   # relaxed mode conserved ARP region databases + training distribution
├── example/            # example structures and expected output
├── notebooks/          # functional prediction notebook, kept as documentation
└── environment.yml
```

---

## Citation

If you use ARG-PASS v2.0, please cite:

> [REFERENCE — not yet available]

For the original framework:

> Bartrop, L., Beauchemin-Lauzon, E., Grenier, F., Rodrigue, S., & Haraoui, L.-P. (2026). 
> Conserved protein sequence-structure signatures identify antibiotic resistance genes from the human microbiome. 
> Microbiome, 14(1), 218. https://doi.org/10.1186/s40168-026-02487-6


ARG-PASS uses Foldseek (v2.0 and lddt). Please also cite:

> van Kempen M, Kim SS, Tumescheit C, Mirdita M, Lee J, Gilchrist CLM, Söding J,
> Steinegger M. Fast and accurate protein structure search with Foldseek.
> *Nature Biotechnology* (2024).

---

## Requirements

- Python ≥ 3.9
- Foldseek ≥ 10
- pandas, numpy, scikit-learn, matplotlib

All installed by `environment.yml`.

Tested on Linux (Ubuntu 20.04). Foldseek is also available for macOS.

---

## Licence

MIT — see [LICENSE](LICENSE).
