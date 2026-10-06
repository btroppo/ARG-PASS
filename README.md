ARG-PASS (Antibiotic Resistance Gene - PAirwise Sequence vs Structure) uses structurally conserved regions of AlphaFold protein structures encoded by ARGs to predict novel ARGs.

# ARG-PASS

> **ARG-PASS v2.0 is in preparation.** It replaces the manual workflow below with a
> command-line tool and two prediction modes. The code is available on the
> [`v2.0-dev` branch](https://github.com/btroppo/ARG-PASS/tree/v2.0-dev) for testing;
> it is not yet peer-reviewed and results shouldn't be cited pending publication.
> This page documents v1.0, as published in Bartrop, L., Beauchemin-Lauzon, E., Grenier, F., Rodrigue, S., & Haraoui, L.-P. (2026). Conserved protein sequence-structure signatures identify antibiotic resistance genes from the human microbiome. Microbiome, 14(1), 218. https://doi.org/10.1186/s40168-026-02487-6
.

## Requirements for ARG-PASS

### System tools
- Foldseek (latest)
- FoldMason Release 2-7bd21ed (pinned — see note below)
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

To run the ARG-PASS pipeline in full and reproduce figures from the pre-print go to [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19038120.svg)](https://doi.org/10.5281/zenodo.19038120) and follow the README there. To simply run an example here follow instructions below:

Clone the repository and install structure alignment tools in a conda environment:
```bash
git clone https://github.com/btroppo/ARG-PASS.git
cd ARG-PASS

# Create conda environment and install foldseek
conda create -n argpass -c conda-forge -c bioconda foldseek python=3.9 jupyter
conda activate argpass

# Install pinned FoldMason version
wget https://github.com/steineggerlab/foldmason/releases/download/2-7bd21ed/foldmason-linux-avx2.tar.gz
tar xvzf foldmason-linux-avx2.tar.gz

# Add FoldMason to PATH permanently for this environment
echo 'export PATH="$(pwd)/foldmason/bin/:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installations
foldseek --version
foldmason --version

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
