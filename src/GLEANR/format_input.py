"""Format input file to meet GLEANR's requirements."""

import sys

import numpy as np
import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def format_effect(data, snp_list, phenotypes, out):
    """Format effect sizes matrix."""
    df = (
        data.filter(pl.col("rsID").is_in(snp_list))
        .rename({"rsID": "SNP"})
        .drop_nulls()
        )
    df.write_csv(out,
                 separator=' ',
                 null_value="NA")
    return df

def format_se(data, traits, out):
    """Format standard error estimates matrix."""
    n_rows, n_cols = data.shape
    df = pl.DataFrame(np.ones((n_rows, n_cols - 1)),
                      schema=traits)
    df = pl.concat([data.select("SNP"), df], how="horizontal")
    df.write_csv(out,
              separator=' ',
                 null_value="NA")

def format_corr(cov_data, out):
    """Format correlation matrix."""
    df = (
        pl.read_csv(cov_data, has_header=True)
        .drop("")
        )

    df.write_csv(out,
                 separator=' ',
                 null_value="NA")

if __name__ == "__main__":
    # Parameters
    _, PHENOTYPES_PATH, JASS_SUMSTAT_PATH, COV_PATH = sys.argv[:-4]
    CLUMP_OUT, EFFECT_OUT, SE_OUT, C_OUT = sys.argv[-4:]
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)
    DATA = pl.read_csv(JASS_SUMSTAT_PATH)

    # Selection
    SELECTED_SNP = read_phenotypes(CLUMP_OUT)

    # Method
    effect_matrix = format_effect(DATA, SELECTED_SNP, PHENOTYPES, EFFECT_OUT)
    format_se(effect_matrix, PHENOTYPES, SE_OUT)
    format_corr(COV_PATH, C_OUT)
