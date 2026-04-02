# Download necessary additional files #

# Files
## Global reference panel (HDL)
mkdir -p ./data/HDL
wget -c -t 1 https://www.dropbox.com/s/6js1dzy4tkc3gac/UKB_imputed_SVD_eigen99_extraction.tar.gz?dl=0 --no-check-certificate -O ./data/HDL/UKB_imputed_SVD_eigen99_extraction.tar.gz
tar -xzvf ./data/HDL/UKB_imputed_SVD_eigen99_extraction.tar.gz
rm ./data/HDL/UKB_imputed_SVD_eigen99_extraction.tar.gz

## Local reference panel (HDL-L)
source "./config/HDL_arguments.txt"
module load R/4.4.0

mkdir -p ./data/HDL-L
wget https://zenodo.org/records/17904964/files/bim.zip -O ./data/HDL-L/bim.zip
wget https://zenodo.org/records/17904964/files/LD.zip -O ./data/HDL-L/LD.zip
unzip ./data/HDL-L/bim.zip -d ./data/HDL-L
unzip ./data/HDL-L/LD.zip -d ./data/HDL-L
rm ./data/HDL-L/bim.zip ./data/HDL-L/LD.zip

Rscript ./src/common/regions.R $local_panel_dir $regions

module unload R/4.4.0

## GRCh38 positions map (SUPERGNOVA)
source "./config/SUPERGNOVA_arguments.txt"
if $extrapolate_pos
then
    mkdir -p ./$data_dir/SUPERGNOVA
    wget https://storage.googleapis.com/broad-alkesgroup-public/Eagle/downloads/tables/genetic_map_hg38_withX.txt.gz -O $pos_map
    gunzip ./data/SUPERGNOVA/genetic_map_hg38_withX.txt.gz -d ./data/SUPERGNOVA/
fi

## Local partition (SUPERGNOVA from HDL-L)
mkdir -p $data_dir/partition
new_header="chr\tstart\tstop"
for c in $(seq 1 22);
do
    out=${partition/\@/$c}
    echo -e "$new_header" > $out
    cat $regions | grep "^[0-9]*,$c," | awk -F',' -v OFS='\t' '{print $2, $4, $5}' >> $out
done