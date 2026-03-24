#!/bin/bash
#SBATCH --job-name=SUPERGNOVA_run
#SBATCH --mem=30G
#SBATCH -c 16

# Input
source "./config/SUPERGNOVA_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
f1="${list[0]}"
f2="${list[1]}"
n1="${list[2]}"
n2="${list[3]}"
out="${list[4]}"

# Method
python3 ./module/SUPERGNOVA/supergnova.py ${sumstat_in/@/$f1} ${sumstat_in/@/$f2} \
--N1 $n1 \
--N2 $n2 \
--bfile $bfiles \
--partition $partition \
--thread 16 \
--out ${sumstat_out/@/$out}
