# Prepare data for HDL input #

echo "Starting at: $(date)."

# Input
source "./config/HDL_arguments.txt"
mapfile -t studies < $studies_path
mkdir -p $data_dir/sumstats

# Method
## Step 1: format sumstats
echo "Formatting GWAS summary statistics."

new_header="chrom\tSNP\tpos\tA1\tA2\tZ\tP\tN"
for study in "${studies[@]}"; do

    # Avoid problems with A0/A1 renaming to A1/A2
    temp_file="$study.tmp"
    echo -e "$new_header" > $temp_file
    tail -n +2 "$ref_data_dir/$study.txt" >> $temp_file

    Rscript ./module/HDL/HDL.data.wrangling.R \
            gwas.file=$temp_file \
            LD.path=$global_panel_dir \
            SNP=SNP A1=A1 A2=A2 N=N Z=Z \
            output.file=${sumstat/@/$study}

    rm $temp_file
done

## Step 2: create description file
echo "Creating description file."
python3 ./src/HDL/create_description_file.py $studies_path $sumstat $pair $description

echo "Ending at: $(date)."
