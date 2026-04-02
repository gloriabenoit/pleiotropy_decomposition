# Pleiotropy Decomposition Pipeline: Running methods #

source "./config/pipeline_arguments.txt"
module load Python/3.13.2 R/4.4.0

# Running
## HDL and HDL-L
echo "Running HDL and HDL-L."
R_LIBS_USER=./env/hdl; export R_LIBS_USER
sh ./src/HDL/run.sh
sh ./src/HDL-L/run.sh

## SUPERGNOVA
echo "Running SUPERGNOVA."
module unload Python/3.13.2
module load Python/3.8.18
source ./env/supergnova/bin/activate
sh ./src/SUPERGNOVA/run.sh
deactivate
module unload Python/3.8.18
module load Python/3.13.2

## FactorGo
echo "Running FactorGo."
source ./env/factorgo/bin/activate
sh ./src/FactorGo/run.sh |& tee ./log/$prefix/FactorGo/run.log
deactivate

## GFA
echo "Running GFA."
R_LIBS_USER=./env/gfa; export R_LIBS_USER
sh ./src/GFA/run.sh |& tee ./log/$prefix/GFA/run.log

## GLEANR
echo "Running GLEANR."
R_LIBS_USER=./env/gleanr; export R_LIBS_USER
sh ./src/GLEANR/run.sh |& tee ./log/$prefix/GLEANR/run.log

## GUIDE
echo "Running GUIDE."
source ./env/guide/bin/activate
sh ./src/GUIDE/run.sh |& tee ./log/$prefix/GUIDE/run.log
deactivate

R_LIBS_USER=""; export R_LIBS_USER
module unload Python/3.13.2 R/4.4.0
