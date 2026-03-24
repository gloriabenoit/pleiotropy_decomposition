# Run HDL #

# Input
source "./config/HDL_arguments.txt"
mkdir -p $out_dir/output

# Parameters
n_jobs=$(wc -l < $description)

# Method
sbatch -p $slurm_p \
       --array=1-$n_jobs%20 \
       --output="./log/HDL/$prefix.run.%A_%a.out" \
       --error="./log/HDL/$prefix.run.%A_%a.err" \
       ./src/HDL/parallelize_run.sh
