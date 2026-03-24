"""Format input file to meet GUIDE's requirements."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def format_zscore(data, out, snp_list=""):
    """Format Zscore file."""
    df = data.drop_nulls()

    if snp_list:
        df = df.filter(pl.col("rsID").is_in(snp_list))

    df.write_csv(out)

if __name__ == "__main__":
    # Parameters
    _, JASS_SUMSTAT, ZSCORE_OUT = sys.argv[:3]
    if len(sys.argv) == 4:
        SNP_LIST = sys.argv[3]
    else:
        SNP_LIST = ""
    DATA = pl.read_csv(JASS_SUMSTAT)

    # Method
    if SNP_LIST:
        SELECTED_SNP = read_phenotypes(SNP_LIST)
    else:
        SELECTED_SNP=""

    format_zscore(DATA, ZSCORE_OUT, snp_list=SELECTED_SNP)
