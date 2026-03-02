# This is a documented workflow
# Commands are intended to be executed step-by-step manually. Potential qARP class B1-B2 beta-lactamases with best 0-25% seqID to known ARGs are used as an example throughout
# Commands have already been run for the example so re-running commands will overwrite files
# For functional prediction of queries only (without creating high_lddt ARP structures), start from Step 6

# Run all steps from the repo root (ARG-PASS/)
REPO_ROOT=$PWD

# Activate conda environment
conda activate argpass

# Step 2: Sort ARP structure files into clusters (folders): use sort_clusters.ipynb
cd $REPO_ROOT/example/class_B1_B2_BL
jupyter nbconvert --to notebook --inplace --execute sort_clusters.ipynb

# Step 3: FoldMason MSTA on each cluster (with 3 or more representatives) and extract per-column lDDT scores
cd $REPO_ROOT/example/class_B1_B2_BL/cluster_20/Q9RMI1
foldmason easy-msa *.pdb msta tmp --report-mode 1
grep -Eo '"scores": \[(.*)\]' msta.html > col_lddt.txt

# Step 4: Extract residues for each structure in each MSTA to create high-lDDT ARP structures: use create_high_lddt_pdbs.ipynb
cd $REPO_ROOT/example/class_B1_B2_BL/cluster_20/Q9RMI1
mkdir -p high_lddt_subjects
jupyter nbconvert --to notebook --inplace --execute create_high_lddt_pdbs.ipynb

# Step 5: Create Foldseek database and perform pairwise seqID vs TM-score analysis of high_lddt ARP structures created for each cluster
cd $REPO_ROOT/example/class_B1_B2_BL/cluster_20/Q9RMI1/high_lddt_subjects
mkdir -p database
foldseek createdb *.pdb database/high_lddt_subjects.pdb
foldseek easy-search *.pdb database/high_lddt_subjects.pdb subjects.out --alignment-type 1 tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 6: Get highest seqID of query. pdb files to all ARP structures of ARG class, for cluster level assignment (see Methods of paper). In this example the queries are assigned to the 20% seqID clusters of class B1_B2 beta-lactamases. 
# place your own query .pdb files in $REPO_ROOT/example/class_B1_B2_BL/cluster_XX/representative/high_lddt_subjects/queries/
cd $REPO_ROOT/example/class_B1_B2_BL
mkdir -p class_B1_B2_B3_database
foldseek createdb *.pdb class_B1_B2_B3_database/ARP_subjects.pdb
foldseek easy-search *.pdb class_B1_B2_B3_database/ARP_subjects.pdb queries/queries_subjects.out tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 7: Pairwise seqID and TM-score analysis of queries against high_lddt ARP structures
cd $REPO_ROOT/example/class_B1_B2_BL/cluster_20/Q9RMI1/high_lddt_subjects
foldseek easy-search queries/*.pdb database/high_lddt_subjects.pdb queries/queries_tmalign.out --alignment-type 1 tmp --exhaustive-search --format-output "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

# Step 8: Training the one-class SVM on distribution from Step 5 and functional prediction of queries: use functional_prediction.ipynb
cd $REPO_ROOT/example/class_B1_B2_BL/cluster_20/Q9RMI1/high_lddt_subjects
mkdir -p output
jupyter nbconvert --to notebook --inplace --execute functional_prediction.ipynb

# Results (functional predictions.csv and visualisation figures) for each cluster saved to $REPO_ROOT/ARG_class/cluster_XX/representative/high_lddt_subjects/output 
