"""Score variants pleiotropy."""

import sys

from functools import reduce

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

def score_pleiotropy(studies, directory, variants, p_thresh, output):
    """Score variant pleiotropy.

    Parameters
    ----------
    studies : list
        Input studies.
    directory : str
        JASS cleaned GWAS directory.
    variants : list
        Selected variants.
    p_thresh : float
        P-value significance threshold (under).
    output : str
        Pleiotropy scores output path.

    Returns
    -------
    tsv file
        Variants as rows and information as columns:
        rsID,
        score (Pleiotropy score).
    """
    dfs = []

    for filename in studies:
        df = (
            pl.read_csv(f"{directory}/{filename}.txt",
                         separator="\t",
                         columns=["rsID", "P"])
            .filter(pl.col("rsID").is_in(variants))
            .rename({"P": filename})
              )

        dfs.append(df)

    complete_data = reduce(
        lambda left, right: left.join(right,
                                      on="rsID",
                                      how="full",
                                      coalesce=True),
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
        (1 - ((1 / (len(studies) + 1)) * pl.col("count_signif"))).alias("score")
    )

    complete_data.select(["rsID", "score"]).write_csv(output,
                                                      separator="\t")

if __name__ == "__main__":
    # Parameters
    _, STUDIES_PATH, REF_DATA_DIR, INPUT_VARIANTS, OUT, P_THRESH = sys.argv
    STUDIES = read_list_in_file(STUDIES_PATH)

    # Selection
    VARIANTS = read_list_in_file(INPUT_VARIANTS)

    # Method
    score_pleiotropy(STUDIES, REF_DATA_DIR, VARIANTS, float(P_THRESH), OUT)
