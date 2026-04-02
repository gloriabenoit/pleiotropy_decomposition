# Run SUPERGNOVA #

# Input
source "./config/SUPERGNOVA_arguments.txt"
mkdir -p $out_dir/output

# Parameters
n_jobs=$(wc -l < $description)

# Method
sbatch -p $slurm_p \
       --array=1-$n_jobs%20 \
       --output="./log/$prefix/SUPERGNOVA/run-%A/%a.log" \
       ./src/SUPERGNOVA/parallelize_run.sh
