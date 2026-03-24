# Prepare data for HDL input #

# Input
source "./config/HDL_arguments.txt"
mapfile -t phenotypes < $phenotypes_path
mkdir -p $data_dir/sumstats

# Method
## Step 1: format sumstats
echo "Formatting GWAS summary statistics."

new_header="chrom\tSNP\tpos\tA1\tA2\tZ\tP\tN"
for pheno in "${phenotypes[@]}"; do

    # Avoid problems with A0/A1 renaming to A1/A2
    temp_file="$pheno.tmp"
    echo -e "$new_header" > $temp_file
    tail -n +2 "$ref_data_dir/$pheno.txt" >> $temp_file

    # if $use_filters
    # then
    #     python3 ./src/HDL/format_input.py $ref_data_dir/$pheno.txt $temp_file
    # else
    #     echo "Selecting specific SNPs as input"
    #     python3 ./src/HDL/format_input.py $ref_data_dir/$pheno.txt $temp_file $snp_path
    # fi

    Rscript ./module/HDL/HDL.data.wrangling.R \
            gwas.file=$temp_file \
            LD.path=$global_panel_dir \
            SNP=SNP A1=A1 A2=A2 N=N Z=Z \
            output.file=${sumstat/@/$pheno}

    rm $temp_file
done

## Step 2: create description file
echo "Creating description file."
python3 ./src/HDL/create_description_file.py $phenotypes_path $sumstat $description $parameters
