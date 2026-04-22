# Prepare data for FactorGo input #

echo "Starting at: $(date)."

# Input
source "./config/FactorGo_arguments.txt"
mapfile -t studies < $studies_path
mkdir -p $data_dir

# Method
if $use_filters
then
    echo "Using FactorGo's original filters."

    ## Step 1: select pleiotropic SNPs
    echo "Selecting significant pleiotropic variants."
    python3 ./src/FactorGo/select_significant_pleiotropic_variants.py $studies_path $ref_data_dir $p_thresh $min_study $signif_pleio

    ## Step 2: LD prune
    echo "LD pruning."
    files=()
    for study in "${studies[@]}"; do
        files+=("$ref_data_dir/${study}.txt")
    done
    clump_input=$(IFS=, ; echo "${files[*]}")

    plink --bfile $ref_panel \
        --clump $clump_input \
        --extract $signif_pleio \
        --exclude $mhc_snps.snplist \
        --clump-snp-field rsID \
        --clump-field P \
        --clump-r2 $r2_thresh \
        --clump-kb $clump_kb \
        --out $clump
    awk 'NR>1 { if ($3) print $3 }' $clump.clumped > $clump_out

    ## Step 3: format input files
    echo "Formatting input files."
    python3 ./src/FactorGo/format_input.py $all_sample $all_zscore $clump_out $sample $zscore
else
    echo "Selecting specific SNPs as input"

    echo "Formatting input files."
    python3 ./src/FactorGo/format_input.py $all_sample $all_zscore $input_variants $sample $zscore
fi

echo "Ending at: $(date)."
