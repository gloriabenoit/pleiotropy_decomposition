"""Create a HDL pipeline description file."""

import itertools
import sys

def read_list_in_file(filename):
    """Read list of item in file.

    Parameters
    ----------
    filename : str
        File path.

    Returns
    -------
    list
        Found items.
    """
    with open(filename, 'r') as file_in:
        return [line.strip() for line in file_in]

def create_description(studies, filename, pair, output):
    """Create HDL description file.

    Parameters
    ----------
    studies : list
        Input studies.
    filename : str
        Input summary statistics path.
    pair : str
        Pair output path.
    output : str
        Description output path.

    Returns
    -------
    single-space-separated file
        Pairs as rows and information as columns (no header):
        First study path,
        Second study path,
        Pair output path.
    """
    # Per pair
    with open(output, 'w') as description:
        for s1, s2 in itertools.combinations(studies, 2):
            s1_file = f"{filename.replace('@', s1)}"
            s2_file = f"{filename.replace('@', s2)}"
            out = pair.replace('@', s1, 1).replace('@', s2)

            description.write(f"{s1_file}.hdl.rds {s2_file}.hdl.rds {out}\n")

if __name__ == "__main__":
    # Input
    _, STUDIES_PATH, SUMSTAT_FILE, PAIR_FILE, DESCRIPTION = sys.argv
    STUDIES = read_list_in_file(STUDIES_PATH)

    # Method
    create_description(STUDIES, SUMSTAT_FILE, PAIR_FILE, DESCRIPTION)
