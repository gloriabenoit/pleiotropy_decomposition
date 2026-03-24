"""Save sample sizes and zscores for selected phenotypes."""

import sys
from functools import reduce

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def read_sample_sizes(phenotypes, filename):
    """Read JASS meta data file."""
    keep_col = ["filename", "Consortium", "Outcome", "Nsample"]
    df = pl.read_csv(filename,
                          separator="\t",
                          has_header=True,
                          columns=keep_col)

    df = df.with_columns(
        (pl.lit("z_") + pl.concat_str(
            [
                pl.col("Consortium"),
                pl.col("Outcome")
            ], separator = "_"
        )).alias("ID")
    )

    df = df.filter(pl.col("ID").is_in(phenotypes))

    # Reorder lines
    order_map = {value: idx for idx, value in enumerate(phenotypes)}
    df = df.with_columns(
        pl.col("ID")
        .replace(order_map)
        .cast(pl.Int32)
        .alias("order")
    )
    df = df.sort("order")

    df = df.select(["ID", "Nsample"])
    df = df.rename({"Nsample": "N"})

    return df

def read_zscores(phenotypes, directory):
    """Read JASS results to aggregate all zscores."""
    dfs = []
    for filename in phenotypes:
        df = (
            pl.read_csv(f"{directory}/{filename}.txt", separator="\t")
            .select(["rsID", "Z"])
            .rename({"Z": filename})
        )
        dfs.append(df)

    df_final = reduce(
        lambda left, right: left.join(right,
                                        on="rsID",
                                        how="full",
                                        coalesce=True), dfs
    )
    return df_final

def save_common_files(samples, zscores, pheno_sample_out, pheno_zscore_out):
    """Save phenotypes info and zscores."""
    samples.write_csv(pheno_sample_out)
    zscores.write_csv(pheno_zscore_out)

if __name__ == "__main__":
    # Parameters
    _, PHENOTYPES_PATH, META_DATA, HARMONIZED_DIR, PHENO_SAMPLE_OUT, PHENO_ZSCORE_OUT = sys.argv

    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    samples = read_sample_sizes(PHENOTYPES, META_DATA)
    zscores = read_zscores(PHENOTYPES, HARMONIZED_DIR)
    save_common_files(samples, zscores, PHENO_SAMPLE_OUT, PHENO_ZSCORE_OUT)
