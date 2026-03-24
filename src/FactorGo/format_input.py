"""Format input file to meet FactorGo's requirements."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def format_zscore(data, snp_list, out):
    """Format Zscore file."""
    df = data.filter(pl.col("rsID").is_in(snp_list))
    df = df.rename({"rsID": "rsid"})
    df = df.drop_nulls()

    df.write_csv(out,
                 separator='\t')

def format_sample(data, out):
    """Format SampleN file."""
    df = data.with_columns([data["N"].cast(pl.Int64)])

    df.write_csv(out,
                 separator='\t')

if __name__ == "__main__":
    # Parameters
    _, JASS_SUMSTAT, JASS_SAMPLE, SNP_LIST = sys.argv[:-2]
    ZSCORE_OUT, SAMPLE_N_OUT = sys.argv[-2:]
    DATA = pl.read_csv(JASS_SUMSTAT)
    INFO = pl.read_csv(JASS_SAMPLE, columns=["N"])

    # Selection
    SELECTED_SNP = read_phenotypes(SNP_LIST)

    # Method
    format_zscore(DATA, SELECTED_SNP, ZSCORE_OUT)
    format_sample(INFO, SAMPLE_N_OUT)
