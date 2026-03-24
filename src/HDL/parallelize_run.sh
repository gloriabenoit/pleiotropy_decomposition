#!/bin/bash
#SBATCH --job-name=HDL_run
#SBATCH --output=./log/HDL/run_%A_%a.out
#SBATCH --error=./log/HDL/run_%A_%a.err
#SBATCH --mem=35G
#SBATCH -c 8

# Input
source "./config/HDL_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
t1="${list[0]}"
t2="${list[1]}"
out="${list[2]}"

gwas1="${sumstat/@/$t1}.hdl.rds"
gwas2="${sumstat/@/$t2}.hdl.rds"

# Method
Rscript ./module/HDL/HDL.parallel.run.R \
        gwas1.df=$gwas1 \
        gwas2.df=$gwas2 \
        LD.path=$global_panel_dir \
        Nref=$nref \
        output.file=$out_dir/output/$out \
        numCores=8
