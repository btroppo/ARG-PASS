#!/bin/bash
# workflow.sh
# This file documents the analysis workflow
# Commands should be run in appropriate directories

REPO_ROOT=~/ARG-PASS

# Step 1: Foldseek cluster ARP structures at 20%, 30%, and 50% seqID. Example for 20% seqID cluster 
cd $REPO_ROOT/example/sub_class_B3_BL
foldseek easy-cluster *.pdb 20 tmp --min-seq-id 0.2

# Step 2: Sort ARP structure files into clusters (folders)
cd $REPO_ROOT/notebooks
jupyter nbconvert --execute sort_clusters.ipynb

# Step 3: FoldMason MSTA on each cluster (with 3 or more representatives) and extract per-column lDDT scores
cd $REPO_ROOT/example/sub_class_B3_BL/cluster_20/AF-A0A1L6K5Y8-F1-model_v4
foldmason easy-msa *.pdb msta tmp --report-mode 1
grep -Eo '"scores": \[(.*)\]' msta.html > col_lddt.txt

# Step 4: Extract residues for each structure in each MSTA to create high-lDDT ARP structures: use create_high-lDDT_pdbs.ipynb
cd $REPO_ROOT/notebooks
jupyter nbconvert --execute create_high-lDDT_pdbs.ipynb

# Step 5: Create Foldseek database and perform pairwise seqID vs TM-score analysis of high-lDDT ARP structures created for each cluster
cd $REPO_ROOT/example/sub_class_B3_BL/cluster_20/AF-A0A1L6K5Y8-F1-model_v4/high_lddt_subjects
foldseek createdb *.pdb database/high_lddt_subjects.pdb
foldseek easy-search *.pdb database/high_lddt_subjects.pdb subjects.out --alignment-type 1 tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 6: Get highest seqID of queries to all ARP structures for cluster level assignment. In this example the two queries are assigned to the 20% seqID clusters (<25% seqID to an ARP structure)
cd $REPO_ROOT/example/sub_class_B3_BL
foldseek createdb *.pdb database/ARP_subjects.pdb
cd $REPO_ROOT/example/sub_class_B3_BL/cluster_20/AF-A0A1L6K5Y8-F1-model_v4/high_lddt_subjects/queries
foldseek easy-search *.pdb $REPO_ROOT/example/sub_class_B3_BL/database/ARP_subjects.pdb queries_subjects.out tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 7: Pairwise seqID and TM-score analysis of queries against high-lDDT ARP structures
cd $REPO_ROOT/example/sub_class_B3_BL/cluster_20/AF-A0A1L6K5Y8-F1-model_v4/high_lddt_subjects/queries
foldseek easy-search *.pdb $REPO_ROOT/example/sub_class_B3_BL/cluster_20/AF-A0A1L6K5Y8-F1-model_v4/high_lddt_subjects/database/high_lddt_subjects.pdb queries_tmalign.out --alignment-type 1 tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 8: Training the one-class SVM on distribution from Step 5 and functional prediction: use functional_prediction.ipynb
cd $REPO_ROOT/notebooks
jupyter nbconvert --execute functional_prediction.ipynb

