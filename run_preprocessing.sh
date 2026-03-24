# Pleiotropy Decomposition Pipeline: Preprocessing #

echo "Starting preprocessing at: $(date)."

source "./config/pipeline_arguments.txt"
module load Python/3.13.2 R/4.4.0 plink/1.90p
source ./env/processing/bin/activate

## Common files
# echo "Processing common files."
# mkdir -p ./log/
# sh ./src/common/save_common.sh | tee ./log/$prefix.common_files.log

## LDSC
# echo "Processing LDSC results."
# mkdir -p ./log/LDSC/
# sh ./src/LDSC/compute_results.sh | tee ./log/LDSC/$prefix.assembly.log

# ## HDL and HDL-L
# echo "Preprocessing HDL and HDL-L input."
# mkdir -p ./log/HDL/
# R_LIBS_USER=./env/hdl; export R_LIBS_USER
# sh ./src/HDL/preprocessing.sh |& tee ./log/HDL/$prefix.preprocessing.log

# ## SUPERGNOVA
# echo "Preprocessing SUPERGNOVA input."
# mkdir -p ./log/SUPERGNOVA/
# sh ./src/SUPERGNOVA/preprocessing.sh |& tee ./log/SUPERGNOVA/$prefix.preprocessing.log

## FactorGo
echo "Preprocessing FactorGo input."
mkdir -p ./log/FactorGo/
sh ./src/FactorGo/preprocessing.sh |& tee ./log/FactorGo/$prefix.preprocessing.log

## GFA
echo "Preprocessing GFA input."
R_LIBS_USER=./env/gfa; export R_LIBS_USER
mkdir -p ./log/GFA/
sh ./src/GFA/preprocessing.sh |& tee ./log/GFA/$prefix.preprocessing.log

## GLEANR
echo "Preprocessing GLEANR input."
mkdir -p ./log/GLEANR/
sh ./src/GLEANR/preprocessing.sh |& tee ./log/GLEANR/$prefix.preprocessing.log

## GUIDE
echo "Preprocessing GUIDE input."
mkdir -p ./log/GUIDE/
sh ./src/GUIDE/preprocessing.sh |& tee ./log/GUIDE/$prefix.preprocessing.log

deactivate
R_LIBS_USER=""; export R_LIBS_USER
module unload Python/3.13.2 R/4.4.0 plink/1.90p

echo "Ending preprocessing at: $(date)."