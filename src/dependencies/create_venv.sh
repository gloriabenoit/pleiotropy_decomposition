# Create necessary virtual environnemnts #

# Preprocessing and postprocessing
module load Python/3.13.2
python3 -m venv ./env/processing
source ./env/processing/bin/activate
pip install matplotlib numpy polars scipy seaborn
deactivate
module unload Python/3.13.2

# Methods
## SUPERGNOVA
module load Python/3.8.18
python3 -m venv ./env/supergnova
source ./env/supergnova/bin/activate
python3 -m pip install -r ./src/dependencies/SUPERGNOVA_requirements.txt
deactivate
module unload Python/3.8.18

## HDL and HDL-L
R_LIBS_USER=./env/hdl; export R_LIBS_USER
module load R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp
R_install_packages devtools
Rscript ./src/dependencies/HDL_requirements.R
R_LIBS_USER=""; export R_LIBS_USER
module unload R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp

## FactorGo
module load Python/3.13.2
python3 -m venv ./env/factorgo
source ./env/factorgo/bin/activate
cd ./module/FactorGo
pip install .
cd ../../
deactivate
module unload Python/3.13.2

## GFA
R_LIBS_USER=./env/gfa; export R_LIBS_USER
module load R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp
R_install_packages devtools
Rscript ./src/dependencies/GFA_requirements.R
R_LIBS_USER=""; export R_LIBS_USER
module unload R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp

## GLEANR
R_LIBS_USER=./env/gleanr; export R_LIBS_USER
module load R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp
R_install_packages devtools
Rscript ./src/dependencies/GLEANR_requirements.R
R_LIBS_USER=""; export R_LIBS_USER
module unload R/4.4.0 gcc/9.2.0 libxml2 libiconv freetype fontconfig harfbuzz fribidi curl libpng libtiff libjpeg-turbo libwebp

## GUIDE
module load Python/3.13.2
python3 -m venv ./env/guide
source ./env/guide/bin/activate
python3 -m pip install -r ./src/dependencies/GUIDE_requirements.txt
deactivate
module unload Python/3.13.2
