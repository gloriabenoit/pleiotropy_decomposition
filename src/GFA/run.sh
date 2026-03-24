# Run GFA #

echo "Started running at: $(date)."

# Input
source "./config/GFA_arguments.txt"
mkdir -p $out_dir

# Method
Rscript ./src/GFA/5_run_gfa.R $r_corr_clust $zmat_pruned $seed $out $factors $loadings $pve

echo "Ended running at: $(date)."
