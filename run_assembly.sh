# Pleiotropy Decomposition Pipeline: Assembling results #

source "./config/assembly_arguments.txt"
module load Python/3.13.2
source ./env/processing/bin/activate

# Summarize local correlation results
## HDL
# sh ./src/HDL/compute_results.sh
# sh ./src/HDL-L/compute_results.sh

## SUPERGNOVA
# sh ./src/SUPERGNOVA/compute_results.sh

# Assemble all results
sbatch -p $slurm_p \
       -o "./log/$prefix.assembly.%A.log" \
       ./src/assembly/assemble_res.sh

deactivate
module unload Python/3.13.2
