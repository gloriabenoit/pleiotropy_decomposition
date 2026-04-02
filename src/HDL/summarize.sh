# Summarize HDL-L results #

echo "Starting at: $(date)."

# Input
source "./config/HDL_arguments.txt"

# Method
python3 ./src/HDL/summarize_hdl.py $description $summary

echo "Ending at: $(date)."
