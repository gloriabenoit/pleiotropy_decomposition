# Pleiotropy Decomposition Pipeline: Preprocessing data #

echo "Starting preprocessing at: $(date)."

source "./config/pipeline_arguments.txt"
module load Python/3.13.2 R/4.4.0 plink/1.90p
source ./env/processing/bin/activate

## Common files
echo "Processing common files."
mkdir -p ./log/$prefix/
sh ./src/common/save_common.sh | tee ./log/$prefix/common_files.log

# LDSC
echo "Processing LDSC results."
mkdir -p ./log/$prefix/LDSC/
sh ./src/LDSC/processing.sh | tee ./log/$prefix/LDSC/processing.log

## HDL and HDL-L
echo "Preprocessing HDL and HDL-L input."
mkdir -p ./log/$prefix/HDL/
R_LIBS_USER=./env/hdl; export R_LIBS_USER
sh ./src/HDL/preprocessing.sh |& tee ./log/$prefix/HDL/preprocessing.log

## SUPERGNOVA
echo "Preprocessing SUPERGNOVA input."
mkdir -p ./log/$prefix/SUPERGNOVA/
sh ./src/SUPERGNOVA/preprocessing.sh |& tee ./log/$prefix/SUPERGNOVA/preprocessing.log

## FactorGo
echo "Preprocessing FactorGo input."
mkdir -p ./log/$prefix/FactorGo/
sh ./src/FactorGo/preprocessing.sh |& tee ./log/$prefix/FactorGo/preprocessing.log

## GFA
echo "Preprocessing GFA input."
R_LIBS_USER=./env/gfa; export R_LIBS_USER
mkdir -p ./log/$prefix/GFA/
sh ./src/GFA/preprocessing.sh |& tee ./log/$prefix/GFA/preprocessing.log

## GLEANR
echo "Preprocessing GLEANR input."
mkdir -p ./log/$prefix/GLEANR/
sh ./src/GLEANR/preprocessing.sh |& tee ./log/$prefix/GLEANR/preprocessing.log

## GUIDE
echo "Preprocessing GUIDE input."
mkdir -p ./log/$prefix/GUIDE/
sh ./src/GUIDE/preprocessing.sh |& tee ./log/$prefix/GUIDE/preprocessing.log

deactivate
R_LIBS_USER=""; export R_LIBS_USER
module unload Python/3.13.2 R/4.4.0 plink/1.90p

echo "Ending preprocessing at: $(date)."