#!/bin/bash
#SBATCH --job-name=HDL-L_run
#SBATCH --mem=50G
#SBATCH -c 32

echo "Starting run at: $(date)."

# Input
source "./config/HDL_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
s1="${list[0]}"
s2="${list[1]}"
out="${list[2]}"

t1=$(basename "$s1" .hdl.rds)
t2=$(basename "$s2" .hdl.rds)
out="${out/\/HDL\//\/HDL-L\/}"
out="${out/txt/csv}"

# Method
## Run
Rscript ./module/HDL/HDL.L.run.R \
        gwas1.df=$s1 \
        gwas2.df=$s2 \
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

echo "Ending run at: $(date)."
