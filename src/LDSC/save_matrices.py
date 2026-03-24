"""Construct correlation and covariance matrices from LDSC results."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def subset_df(df, phenotypes):
    """Subset phenotypes from global matrix."""
    # Select phenotypes
    df = (
        df.filter(pl.col("").is_in(phenotypes))
        .select([""] + phenotypes)
        )

    # Reorder
    order_map = {k: int(i) for i, k in enumerate(phenotypes)}
    df = (
        df.with_columns(
            pl.col("").replace_strict(order_map, return_dtype=pl.Int16).alias("order")
        )
        .sort("order")
        .drop("order")
    )

    return df

def save_matrix(filename, phenotypes, out):
    """Save LDSC output as a matrix."""
    columns = pl.read_csv(filename,
                          has_header=True,
                          separator="\t",
                          infer_schema_length=False,
                          n_rows=0).columns
    schema = {columns[0]: pl.Utf8}
    schema.update({col: pl.Float64 for col in columns[1:]})

    df = pl.read_csv(filename,
                     separator="\t",
                     has_header=True,
                     columns = [""] + phenotypes,
                     schema=schema
    )

    df = subset_df(df, phenotypes)
    df.write_csv(out)

if __name__ == "__main__":
    # Parameters
    _, PHENOTYPES_PATH, CORR_PATH, COV_PATH, CORR_OUT, COV_OUT = sys.argv

    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    # Correlation
    save_matrix(CORR_PATH, PHENOTYPES, CORR_OUT)

    # Covariance
    save_matrix(COV_PATH, PHENOTYPES, COV_OUT)
