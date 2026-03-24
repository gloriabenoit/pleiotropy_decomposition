# Compute HDL-L results #

# Input
source "./config/HDL_arguments.txt"

# Method
python3 ./src/HDL-L/summarize_hdl.py $out_dir-L $description $total_region $summary_local
