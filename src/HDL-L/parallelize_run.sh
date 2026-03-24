#!/bin/bash
#SBATCH --job-name=HDL-L_run
#SBATCH --output=./log/HDL-L/run_%A_%a.out
#SBATCH --error=./log/HDL-L/run_%A_%a.err
#SBATCH --mem=50G
#SBATCH -c 32

# Input
source "./config/HDL_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
t1="${list[0]}"
t2="${list[1]}"
gwas1="${sumstat/@/$t1}.hdl.rds"
gwas2="${sumstat/@/$t2}.hdl.rds"
out="$t1.$t2$parameters.csv"

# Method
## Run
Rscript ./module/HDL/HDL.L.run.R \
        gwas1.df=$gwas1 \
        gwas2.df=$gwas2 \
        Trait1name=$t1 \
        Trait2name=$t2 \
        LD.path=$local_panel_dir \
        bim.path=$local_bim_dir \
        Nref=$nref \
        N0=0 \
        type="WG" \
        cores=32 \
        save.path=$out_dir-L/output/

## Save output as csv
Rscript ./src/HDL-L/save_res_csv.R $out_dir-L/output $t1 $t2 $out
