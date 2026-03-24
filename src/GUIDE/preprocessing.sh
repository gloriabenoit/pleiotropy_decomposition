# Prepare data for GUIDE input #

# Input
source "./config/GUIDE_arguments.txt"
mkdir -p $data_dir

# Method
echo "Formatting input files."
if $use_filters
then
    python3 ./src/GUIDE/format_input.py $pheno_zscore_out $zscore
else
    echo "Selecting specific SNPs as input."
    python3 ./src/GUIDE/format_input.py $pheno_zscore_out $zscore $snp_path
fi
