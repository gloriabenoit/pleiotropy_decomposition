# Run GLEANR #

echo "Started running at: $(date)."

# Input
source "./config/GLEANR_arguments.txt"
mkdir -p $out_dir

# Method
Rscript ./src/GLEANR/run_gleanr.R $betas $se $cov $out $factors $loadings $pve

echo "Ended running at: $(date)."
