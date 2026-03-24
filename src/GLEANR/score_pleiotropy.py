"""Score pleiotropy of selected SNP."""

import sys
from functools import reduce

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def score_pleiotropy(path, traits, snp_list, p_thresh, out):
    """Score pleiotropy of SNPs."""
    dfs = []

    for filename in traits:
        df = (
            pl.read_csv(f"{path}/{filename}.txt",
                         separator="\t",
                         columns=["rsID", "P"])
            .filter(pl.col("rsID").is_in(snp_list))
            .rename({"P": filename})
              )

        dfs.append(df)

    complete_data = reduce(
        lambda left, right: left.join(right, on="rsID", how="full", coalesce=True),
        dfs)

    pval_cols = [col for col in complete_data.columns if col != "rsID"]

    # Number of significant studies
    complete_data = complete_data.with_columns(
        pl.sum_horizontal(
            [(pl.col(c) < p_thresh).cast(pl.Int64) for c in pval_cols]
        ).alias("count_signif")
    )

    # Pleiotropy score
    complete_data = complete_data.with_columns(
        (1 - ((1 / (len(traits) + 1)) * pl.col("count_signif"))).alias("score")
    )

    complete_data.select(["rsID", "score"]).write_csv(out,
                                                      separator="\t")

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, PHENOTYPES_PATH, SIGNIF_SNPS, OUT, P_THRESH = sys.argv
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    # Selection
    SELECTED_SNP = read_phenotypes(SIGNIF_SNPS)

    # Method
    score_pleiotropy(DATA_DIR, PHENOTYPES, SELECTED_SNP, float(P_THRESH), OUT)
