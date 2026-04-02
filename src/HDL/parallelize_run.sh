#!/bin/bash
#SBATCH --job-name=HDL_run
#SBATCH --mem=35G
#SBATCH -c 8

echo "Starting run at: $(date)."

# Input
source "./config/HDL_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
s1="${list[0]}"
s2="${list[1]}"
out="${list[2]}"

# Method
Rscript ./module/HDL/HDL.parallel.run.R \
        gwas1.df=$s1 \
        gwas2.df=$s2 \
        LD.path=$global_panel_dir \
        Nref=$nref \
        output.file=$out \
        numCores=8

echo "Ending run at: $(date)."
