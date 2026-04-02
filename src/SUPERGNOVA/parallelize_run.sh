#!/bin/bash
#SBATCH --job-name=SUPERGNOVA_run
#SBATCH --mem=30G
#SBATCH -c 16

echo "Starting run at: $(date)."

# Input
source "./config/SUPERGNOVA_arguments.txt"

# Command
line=$(sed "${SLURM_ARRAY_TASK_ID}q;d" $description)
list=($line)
s1="${list[0]}"
s2="${list[1]}"
n1="${list[2]}"
n2="${list[3]}"
out="${list[4]}"

# Method
python3 ./module/SUPERGNOVA/supergnova.py $s1 $s2 \
--N1 $n1 \
--N2 $n2 \
--bfile $bfiles \
--partition $partition \
--thread 16 \
--out $out

echo "Ending run at: $(date)."
