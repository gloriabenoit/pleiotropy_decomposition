# Run GUIDE #

echo "Starting at: $(date)."

# Input
source "./config/GUIDE_arguments.txt"
mkdir -p $out_dir

# Method
python3 ./src/GUIDE/run_guide.py $zscore $k $factors $loadings $pve

echo "Ending at: $(date)."
