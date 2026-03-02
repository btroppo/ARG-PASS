ARG-PASS (Antibiotic Resistance Gene - PAirwise Sequence vs Structure) uses structurally conserved regions of AlphaFold protein structures encoded by ARGs to predict new ARGs. Pre-print available: https://www.biorxiv.org/content/10.1101/2025.10.01.679039v1

<img width="1486" height="855" alt="Copy of Copy of Copy of Copy of bioinfo pipeline3 (2)" src="https://github.com/user-attachments/assets/b753227a-a043-4bc5-8dc9-d34664534bb7" />

## Requirements for ARG-PASS

### System tools
- Foldseek (latest)
- FoldMason (latest)
- Jupyter (latest)
- grep
- bash shell
- tar / zip
- standard Unix utilities (awk, sed, coreutils)

### Python
- Python >= 3.9

### Python packages
- biopython>=1.83
- pandas>=2.2.1
- numpy>=1.26.4
- scipy>=1.12.0
- matplotlib>=3.8.3
- seaborn>=0.13.2
- scikit-learn>=1.4.1

## Running ARG-PASS

To run the ARG-PASS pipeline in full and reproduce figures from the manuscript go to [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18817276.svg)](https://doi.org/10.5281/zenodo.18817276) and follow the README there. To simply run an example here follow instructions below:

Install all dependencies and download databases:
```bash
git clone https://github.com/btroppo/ARG-PASS
cd ARG-PASS
# create conda environment and install structure alignment tools
conda create -n argpass -c conda-forge -c bioconda foldmason foldseek python=3.9 jupyter
conda activate argpass
# Install Python dependencies
pip install -r requirements.txt
```
Then follow the Steps outlined in ARG-PASS/workflow.sh

### Functional prediction of your own queries

To only predict functionality of your own queries, start from Step 6 in ARG-PASS/workflow.sh

### Data structure of example/

Data structured hierarchically as:
ARG class → cluster → representative ARP structure → high_lddt ARP structures → output

Example:
APH/cluster_20/AF-Q08JA6-F1-model_v6/high_lddt_subjects/output

Where:

APH = ARG class, aminoglycoside phospho-transferases. Contains all ARP structures for the ARG class and their Foldseek database, Foldseek cluster output, and queries for functional prediction.

cluster_20 = ARP structure cluster

AF-Q08JA6-F1-model_v6 = representative protein accession for the structure cluster. Contains ARP structure files, raw data from FoldMason MSTA and lDDT scores, and a Jupyter notebook for creation of high-lDDT ARP structures.

high_lddt_subjects = high-lDDT ARP structures. Contains high-lDDT ARP structure files, folder containing qARP structures (queries) from paper, raw data from pairwise Foldseek analysis, Jupyter notebook for one-class SVM training and functional prediction

output = functional prediction results. Contains functional predictions of qARP structures for the specific cluster in a .csv file and figures for visualisation

## Tested on Linux (Ubuntu 20.04)
Foldseek and FoldMason also available for Mac
