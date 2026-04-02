#!/bin/bash
#SBATCH --job-name=pipeline_assembly
#SBATCH --mem=200G
#SBATCH -c 64

echo "Starting at: $(date)."

# Input
source "./config/assembly_arguments.txt"

# Assemble all results
python3 ./src/assembly/merge_variant_results.py \
        $studies_path $ref_data_dir $regions \
        $supergnova_out $hdll_out \
        $factorgo_out $factorgo_variants \
        $gfa_out $gfa_variants \
        $gleanr_out $gleanr_variants \
        $guide_out $guide_variants \
        $final_assembly \
        $use_filters $input_variants

echo "Ending at: $(date)."
