# Prepare data for SUPERGNOVA input #

echo "Starting at: $(date)."

# Input
source "./config/SUPERGNOVA_arguments.txt"
mapfile -t studies < $studies_path
mkdir -p $data_dir

# Method
## Step 1: split reference by chromosome
echo "Splitting reference by chromosomes."
mkdir -p $data_dir/bfiles
for c in $(seq 1 22)
do
    echo "Chromosome $c"
    out=${bfiles/\@/$c}
    if [ ! -f $out.bed ]
    then
        plink --bfile $ref_ld \
                --chr $c \
                --make-bed \
                --out $out
    fi

    ## Step 1.5 (optional): extrapolate positions
    if $extrapolate_pos
    then
        echo "Extrapolating positions."
        python3 ./src/SUPERGNOVA/compute_positions.py $out.bim $pos_map $c
    fi
done

## Step 2: format summary statistics
echo "Formatting input summary statistics."
mkdir -p $data_dir/sumstats

new_header="CHR\tSNP\tpos\tA1\tA2\tZ\tP\tN"
for study in "${studies[@]}"
do
    out="$data_dir/sumstats/$study.txt"
    echo -e "$new_header" > $out
    tail -n +2 "$ref_data_dir/$study.txt" >> $out

done

## Step 3: create description file
echo "Creating description file."
python3 ./src/SUPERGNOVA/create_description_file.py $studies_path $all_sample $sumstat $pair $description

echo "Ending at: $(date)."
