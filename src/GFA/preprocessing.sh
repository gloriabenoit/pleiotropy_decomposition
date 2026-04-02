# Prepare data for GFA input #

echo "Starting at: $(date)."

# Input
source "./config/LDSC_arguments.txt"
source "./config/GFA_arguments.txt"
mkdir -p $zmat_dir

# Method
# Step 1: create description file
echo "Creating description file."
python3 ./src/GFA/create_description_file.py $ref_data_dir $all_sample $description

# Step 2: split reference by chromosome
echo "Splitting reference by chromosomes."
Rscript ./src/GFA/1_combine_and_format.R $description $sample_size_tol $zmat_combined

if $use_filters
then
    echo "Using GFA's original filters."

    # Step 3: LD prune
    echo "LD pruning."
    Rscript ./src/GFA/2_ld_prune_chrom_plink.R $ref_ld $zmat_combined $r2_thresh $clump_kb $p_thresh $ld_prioritization $zmat_pruned $snps
else
    # Step 3: select variants
    echo "Selecting specific SNPs as input."
    Rscript ./src/GFA/2_input_snp_list.R $zmat_combined $input_variants $zmat_pruned
fi

# Step 4: estimation of nuisance correlation
echo "Estimating nuisance correlation R."
Rscript ./src/GFA/3_R_ldsc.R $corr_ldsc $cov_ldsc $zmat_pruned $p_thresh $cond_num $r_estimate

# Step 5: cluster correlated traits
echo "Clustering correlated traits."
Rscript ./src/GFA/4_R_corr_clust.R $r_estimate $cor_clust $cond_num $r_corr_clust

echo "Ending at: $(date)."
