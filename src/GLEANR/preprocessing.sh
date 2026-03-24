# Prepare data for GLEANR input #

# Input
source "./config/LDSC_arguments.txt"
source "./config/GLEANR_arguments.txt"
mkdir -p $data_dir

# Method
if $use_filters
then
    echo "Using GLEANR's original filters"

    ## Step 1: select significant SNPs
    echo "Selecting significant variants."
    python3 ./src/GLEANR/select_significant_SNP.py $ref_data_dir $phenotypes_path $p_thresh $signif_pleio

    ## Step 2: score pleiotropy
    echo "Scoring pleiotropy."
    python3 ./src/GLEANR/score_pleiotropy.py $ref_data_dir $phenotypes_path $signif_pleio $score_pleio $p_thresh

    ## Step 3: LD prune
    echo "LD pruning."
    plink --bfile $ref_ld \
        --clump $score_pleio \
        --exclude $mhc_snps.snplist \
        --clump-snp-field rsID \
        --clump-field score \
        --clump-r2 $r2_thresh \
        --clump-kb $clump_kb \
        --clump-p1 1 \
        --clump-p2 1 \
        --out $clump
    awk 'NR>1 { if ($3) print $3 }' $clump.clumped > $clump_out

    ## Step 4: final matrices generation
    echo "Formatting input files."
    python3 ./src/GLEANR/format_input.py $phenotypes_path $pheno_zscore_out $cov_ldsc $clump_out $betas $se $cov
else
    echo "Selecting specific SNPs as input."

    echo "Formatting input files."
    python3 ./src/GLEANR/format_input.py $phenotypes_path $pheno_zscore_out $cov_ldsc $snp_path $betas $se $cov
fi