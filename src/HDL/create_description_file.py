"""Create a SUPERGNOVA pipeline description file."""

import itertools
import sys

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def create_description(phenotypes, filename, parameters, output):
    """Create description file."""
    # Per pair
    with open(output, 'w') as description:
        for f1, f2 in itertools.combinations(phenotypes, 2):
            f1_file = filename.split('/')[-1].replace('@', f1)
            f2_file = filename.split('/')[-1].replace('@', f2)
            out = f"{f1_file}.{f2_file}{parameters}.txt"

            description.write(f"{f1_file} {f2_file} {out}\n")

if __name__ == "__main__":
    # Input
    _, PHENOTYPES_PATH, SUMSTAT_FILE, DESCRIPTION = sys.argv[:4]
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    PARAMETERS = ""
    if len(sys.argv) == 5:
        PARAMETERS = sys.argv[4]

    # Method
    create_description(PHENOTYPES, SUMSTAT_FILE, PARAMETERS, DESCRIPTION)
