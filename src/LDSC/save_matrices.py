"""Construct correlation and covariance matrices from LDSC results."""

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

def subset_df(studies, df):
    """Subset studies from matrix.
    
    Parameters
    ----------
    studies : list
        Input studies.
    df : polars dataframe
        Matrix.
    """
    # Select studies
    df = (
        df.filter(pl.col("").is_in(studies))
        .select([""] + studies)
        )

    # Reorder
    order_map = {k: int(i) for i, k in enumerate(studies)}
    df = (
        df.with_columns(
            pl.col("").replace_strict(order_map,
                                      return_dtype=pl.Int16).alias("order")
        )
        .sort("order")
        .drop("order")
    )

    return df

def save_ldsc_matrix(studies, filename, out):
    """Save LDSC output as a matrix.

    Parameters
    ----------
    studies : list
        Input studies.
    filename : str
        LDSC global matrix path.
    out : str
        LDSC matrix output path.

    Returns
    -------
    csv file
        LDSC matrix of selected studies.
    """
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
                     columns = [""] + studies,
                     schema=schema
    )

    df = subset_df(studies, df)
    df.write_csv(out)

if __name__ == "__main__":
    # Parameters
    _, STUDIES_PATH, CORR_PATH, COV_PATH, CORR_OUT, COV_OUT = sys.argv

    STUDIES = read_list_in_file(STUDIES_PATH)

    # Correlation
    print("Saving correlation matrix.")
    save_ldsc_matrix(STUDIES, CORR_PATH, CORR_OUT)

    # Covariance
    print("Saving covariance matrix.")
    save_ldsc_matrix(STUDIES, COV_PATH, COV_OUT)
