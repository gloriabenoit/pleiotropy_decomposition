# Summarize HDL-L results #

echo "Starting at: $(date)."

# Input
source "./config/HDL_arguments.txt"

# Method
python3 ./src/HDL-L/summarize_hdll.py $description $total_region $summary

echo "Ending at: $(date)."
