"""Format input file to meet GUIDE's requirements."""

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

def format_effect(df, output, variants=""):
    """Format GUIDE effects file.
    
    Parameters
    ----------
    df : polars dataframe
        Variants as rows and information as columns:
        rsID,
        {Study} (Z-scores) for all studies.
    output : str
        Z-score matrix output path.
    variants : list
        Input variants (Default is empty).
    
    Returns
    -------
    csv file
        Variants as rows and information as columns:
        rsID,
        {Study} (Effects) for all studies.
    """
    effect = df.drop_nulls()

    if variants:
        effect = effect.filter(pl.col("rsID").is_in(variants))

    effect.write_csv(output)

if __name__ == "__main__":
    # Parameters
    _, ALL_ZSCORE, ZSCORE_OUT = sys.argv[:3]
    if len(sys.argv) == 4:
        INPUT_VARIANTS = sys.argv[3]
    else:
        INPUT_VARIANTS = ""
    ZSCORES = pl.read_csv(ALL_ZSCORE)

    # Selection
    if INPUT_VARIANTS:
        VARIANTS = read_list_in_file(INPUT_VARIANTS)
    else:
        VARIANTS=""

    # Method
    format_effect(ZSCORES, ZSCORE_OUT, variants=VARIANTS)
