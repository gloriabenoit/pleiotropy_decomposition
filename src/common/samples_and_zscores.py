"""Save sample sizes and zscores for input studies."""

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

def read_sample_sizes(studies, filename):
    """Read study sample size from JASS meta data file.

    Parameters
    ----------
    studies : list
        Input studies.
    filename : str
        JASS meta data path.

    Returns
    -------
    polars dataframe
        Studies as rows and information as columns:
        ID (Study name),
        N (sample size).
    """
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

    df = df.filter(pl.col("ID").is_in(studies))

    # Reorder lines
    order_map = {study: idx for idx, study in enumerate(studies)}
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

def read_zscores(studies, directory):
    """Read Z-scores from JASS cleaned GWAS.

    Parameters
    ----------
    studies : list
        Input studies.
    directory : str
        JASS cleaned GWAS directory.

    Returns
    -------
    polars dataframe
        Variants as rows and information as columns:
        rsID,
        {Study} (Z-scores) for all studies.
    """
    dfs = []
    for filename in studies:
        print(filename)
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

if __name__ == "__main__":
    # Parameters
    _, STUDIES_PATH, META_DATA, REF_DATA_DIR, ALL_SAMPLE, ALL_ZSCORE = sys.argv

    STUDIES = read_list_in_file(STUDIES_PATH)

    # Sample sizes
    print("Reading sample sizes.")
    samples = read_sample_sizes(STUDIES, META_DATA)
    samples.write_csv(ALL_SAMPLE)

    # Z-scores
    print("Reading Z-scores.")
    zscores = read_zscores(STUDIES, REF_DATA_DIR)
    zscores.write_csv(ALL_ZSCORE)
