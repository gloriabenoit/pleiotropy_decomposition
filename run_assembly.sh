# Pleiotropy Decomposition Pipeline: Assembling results #

source "./config/assembly_arguments.txt"
module load Python/3.13.2
source ./env/processing/bin/activate

# Summarize local correlation results
## HDL
echo "Summarizing HDL results."
sh ./src/HDL/summarize.sh |& tee ./log/$prefix/HDL/summarize.log

## HDL-L
echo "Summarizing HDL-L results."
sh ./src/HDL-L/summarize.sh |& tee ./log/$prefix/HDL-L/summarize.log

## SUPERGNOVA
echo "Summarizing SUPERGNOVA results."
sh ./src/SUPERGNOVA/summarize.sh |& tee ./log/$prefix/SUPERGNOVA/summarize.log

# Assemble all results
echo "Assembling all results."
sbatch -p $slurm_p -o "./log/$prefix/assembly.%A.log" \
       ./src/assembly/assembly.sh

deactivate
module unload Python/3.13.2
