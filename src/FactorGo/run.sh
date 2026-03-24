# Run FactorGo #

echo "Started running at: $(date)."

# Input
source "./config/FactorGo_arguments.txt"
mkdir -p $out_dir

# Method
factorgo \
    $zscore \
    $sample \
    -k $k \
    --scale \
    -o $out

echo "Ended running at: $(date)."
