"""Format input file to meet GLEANR's requirements."""

import sys

import numpy as np
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

def format_effect(df, variants, output):
    """Format GLEANR effect sizes matrix.

    Parameters
    ----------
    df : polars dataframe
        Variants as rows and information as columns:
        rsID,
        {Study} (Z-scores) for all studies.
    variants : list
        Input variants.
    output : str
        Effect sizes matrix output path.

    Returns
    -------
    single-space-separated file
        Variants as rows and information as columns:
        SNP,
        {Study} (Effect sizes) for all studies.
    polars dataframe
        Variants as rows and information as columns:
        SNP,
        {Study} (Effect sizes) for all studies.
    """
    effect = (
        df.filter(pl.col("rsID").is_in(variants))
        .rename({"rsID": "SNP"})
        .drop_nulls()
        )

    effect.write_csv(output,
                 separator=' ',
                 null_value="NA")

    return effect

def format_se(df, output):
    """Format standard error estimates matrix.

    Parameters
    ----------
    df : polars dataframe
        Variants as rows and information as columns:
        SNP,
        {Study} (Effect sizes) for all studies.
    output : str
        Standard error estimates matrix output path.

    Returns
    -------
    single-space-separated file
        Variants as rows and information as columns:
        SNP,
        {Study} (Standard error estimates=1) for all studies.
    """
    n_rows, n_cols = df.shape
    se = pl.DataFrame(np.ones((n_rows, n_cols - 1)),
                      schema=df.columns[1:])
    se = pl.concat([df.select("SNP"), se], how="horizontal")
    se.write_csv(output,
              separator=' ',
                 null_value="NA")

def format_corr(df, output):
    """Format correlation matrix.

    Parameters
    ----------
    df : polars dataframe
        Correlation matrix.
    output : str
        Correlation matrix output path.

    Returns
    -------
    single-space-separated file
        Correlation matrix.
    """
    corr = (
        pl.read_csv(df, has_header=True)
        .drop("")
        )

    corr.write_csv(output,
                 separator=' ',
                 null_value="NA")

if __name__ == "__main__":
    # Parameters
    _, ALL_ZSCORE, COV_PATH = sys.argv[:3]
    INPUT_VARIANTS, EFFECT_OUT, SE_OUT, C_OUT = sys.argv[3:]
    ZSCORES = pl.read_csv(ALL_ZSCORE)

    # Selection
    print("Reading final variant selection.")
    VARIANTS = read_list_in_file(INPUT_VARIANTS)

    # Method
    print("Formatting effect sizes matrix.")
    effect_matrix = format_effect(ZSCORES, VARIANTS, EFFECT_OUT)

    print("Formatting standard error estimates matrix.")
    format_se(effect_matrix, SE_OUT)

    print("Formatting correlation matrix.")
    format_corr(COV_PATH, C_OUT)
