# Prepare data for GUIDE input #

echo "Starting at: $(date)."

# Input
source "./config/GUIDE_arguments.txt"
mkdir -p $data_dir

# Method
echo "Formatting input files."
if $use_filters
then
    python3 ./src/GUIDE/format_input.py $all_zscore $zscore
else
    echo "Selecting specific SNPs as input."
    python3 ./src/GUIDE/format_input.py $all_zscore $zscore $input_variants
fi

echo "Ending at: $(date)."
