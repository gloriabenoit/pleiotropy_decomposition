"""Create a SUPERGNOVA pipeline description file."""

import itertools
import sys

import polars as pl

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

def get_sample_size(df, study):
    """Read study sample size.

    Parameters
    ----------
    df : polars dataframe
        Studies as rows and information as columns:
            ID (Study name),
            N (Sample size).
    study : str
        Study name.

    Returns
    -------
    int
        Study sample size.
    """
    df = df.filter(pl.col("ID") == study)
    size = df.item(0, "N")

    return int(size)

def create_description(studies, df, filename, pair, output):
    """Create SUPERGNOVA description file.

    Parameters
    ----------
    studies : list
        Input studies.
    df : polars dataframe
        Studies as rows and information as columns:
            ID (Study name),
            N (Sample size).
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
        First study sample size,
        Second study sample size,
        Pair output path.
    """
    # Per pair
    with open(output, 'w') as description:
        for s1, s2 in itertools.combinations(studies, 2):
            s1_file = f"{filename.replace('@', s1)}"
            s2_file = f"{filename.replace('@', s2)}"

            n1, n2 = get_sample_size(df, s1), get_sample_size(df, s2)
            out = pair.replace('@', s1, 1).replace('@', s2)
            description.write(f"{s1_file} {s2_file} {n1} {n2} {out}\n")

if __name__ == "__main__":
    # Parameters
    _, STUDIES_PATH, ALL_SAMPLE, SUMSTAT_FILE, PAIR_FILE, DESCRIPTION = sys.argv
    STUDIES = read_list_in_file(STUDIES_PATH)
    SAMPLES = pl.read_csv(ALL_SAMPLE)

    # Method
    create_description(STUDIES, SAMPLES, SUMSTAT_FILE, PAIR_FILE, DESCRIPTION)
