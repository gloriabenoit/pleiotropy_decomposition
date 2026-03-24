#!/bin/bash
#SBATCH --job-name=pipeline_assembly
#SBATCH --mem=200G
#SBATCH -c 64

# Input
source "./config/assembly_arguments.txt"

# Assemble all results
echo "Assembling results"
# python3 ./src/assembly/assemble_snps_res.py $phenotypes_path $ref_data_dir $regions_out \
#                                    $supergnova_out $hdll_out \
#                                    $factorgo_out $factorgo_snps \
#                                    $gfa_out $gfa_snps \
#                                    $gleanr_out $gleanr_snps \
#                                    $guide_out $guide_snps \
#                                    $final_assembly \
#                                    $use_filters $snp_path

# Compute correlations
echo "Computing correlations"
python3 ./src/assembly/compute_corr.py $final_assembly $summary_corr $assembly_corr

# View correlations
echo "Saving heatmap"
python3 ./src/assembly/view_corr.py $assembly_corr $corr_out $corr_cluster_out
