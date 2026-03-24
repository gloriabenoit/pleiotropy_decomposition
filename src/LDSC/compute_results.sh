# Compute LDSC results #

# Input
source "./config/LDSC_arguments.txt"
mkdir -p $out_dir

# Method
echo "Saving LDSC results."
python3 ./src/LDSC/save_matrices.py $phenotypes_path $corr_path $cov_path $corr_ldsc $cov_ldsc
