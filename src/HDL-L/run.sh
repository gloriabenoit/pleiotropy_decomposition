# Run HDL #

# Input
source "./config/HDL_arguments.txt"
mkdir -p $out_dir-L/output

# Parameters
n_jobs=$(wc -l < $description)

# Method
sbatch -p $slurm_p \
       --array=1-$n_jobs%20 \
       --output="./log/$prefix/HDL-L/run-%A/%a.log" \
       ./src/HDL-L/parallelize_run.sh
