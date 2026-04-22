# Compute pipeline common files #

echo "Starting at: $(date)."

# Input
source "./config/pipeline_arguments.txt"

# Method
## Get MHC region variants to exclude
echo "List variants in MHC region."
plink --bfile $ref_panel \
    --chr 6 \
    --from-bp $mhc_start \
    --to-bp $mhc_end \
    --write-snplist \
    --out $mhc_snps
rm $mhc_snps.nosex
rm $mhc_snps.log

## Get sample sizes and zscores
echo "Saving sample sizes and zscores."
python3 ./src/common/samples_and_zscores.py $studies_path $meta_data_path $ref_data_dir $all_sample $all_zscore

echo "Ending at: $(date)."
