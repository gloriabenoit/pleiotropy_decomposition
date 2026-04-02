# Summarize SUPERGNOVA results #

echo "Starting at: $(date)."

# Input
source "./config/SUPERGNOVA_arguments.txt"

# Method
python3 ./src/SUPERGNOVA/summarize_supergnova.py $description $total_region $summary

echo "Ending at: $(date)."
