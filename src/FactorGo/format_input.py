"""Format input file to meet FactorGo's requirements."""

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

def format_sample(df, output):
    """Format FactorGo Sample size file.

    Parameters
    ----------
    df : polars dataframe
        Studies as rows and information as columns:
        ID (Study name),
        N (Sample size).
    output : str
        Correlation matrix output path.

    Returns
    -------
    file
        Studies as rows and sample sizes as column:
        N.
    """
    samples = df.with_columns([df["N"].cast(pl.Int64)])

    samples.write_csv(output)

def format_zscore(df, variants, output):
    """Format FactorGo Z-score file.

    Parameters
    ----------
    df : polars dataframe
        Variants as rows and information as columns:
        rsID,
        {Study} (Z-scores) for all studies.
    variants : list
        Input variants.
    output : str
        Z-score matrix output path.

    Returns
    -------
    tsv file
        Variants as rows and information as columns:
        rsid,
        {Study} (Z-scores) for all studies.
    """
    zscore = df.filter(pl.col("rsID").is_in(variants))
    zscore = zscore.rename({"rsID": "rsid"})
    zscore = zscore.drop_nulls()

    zscore.write_csv(output, separator='\t')

if __name__ == "__main__":
    # Parameters
    _, ALL_SAMPLE, ALL_ZSCORE, INPUT_VARIANTS = sys.argv[:4]
    SAMPLE_OUT, ZSCORE_OUT = sys.argv[4:]
    SAMPLES = pl.read_csv(ALL_SAMPLE, columns=["N"])
    ZSCORES = pl.read_csv(ALL_ZSCORE)

    # Selection
    print("Reading final variant selection.")
    VARIANTS = read_list_in_file(INPUT_VARIANTS)

    # Method
    print("Formatting sample size file.")
    format_sample(SAMPLES, SAMPLE_OUT)

    print("Formatting Z-score file.")
    format_zscore(ZSCORES, VARIANTS, ZSCORE_OUT)
