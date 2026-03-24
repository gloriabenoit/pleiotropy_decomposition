# Compute pipeline common files #

echo "Started processing at: $(date)."

# Input
source "./config/pipeline_arguments.txt"

# Method
## Get MHC region variants to exclude
echo "List variants in MHC region."
plink --bfile $ref_ld \
    --chr 6 \
    --from-bp $mhc_start \
    --to-bp $mhc_end \
    --write-snplist \
    --out $mhc_snps
rm $mhc_snps.nosex
rm $mhc_snps.log

## Get sample sizes and zscores
echo "Saving sample sizes and zscores."
python3 ./src/common/samples_and_zscores.py $phenotypes_path $meta_data_path $ref_data_dir $pheno_sample_out $pheno_zscore_out

echo "Ended processing at: $(date)."
