"""Summarize HDL-L results."""

import sys

import polars as pl

HDLL_HEADER = ["STUDY1", "STUDY2",
              "AVG_H1", "AVG_H1_P", "AVG_H2", "AVG_H2_P",
              "AVG_COV", "AVG_CORR", "AVG_P",
              "NEG_REGION", "POS_REGION",
              "N_REGION", "PROP_REGION"]

HDLL_SCHEMA = {"Trait1": pl.String,
              "Trait2": pl.String,
              "chr": pl.Int64,
              "piece": pl.Int64,
              "eigen_use": pl.Float64,
              "Heritability_1": pl.Float64,
              "P_value_Heritability_1": pl.Float64,
              "Heritability_2": pl.Float64,
              "P_value_Heritability_2": pl.Float64,
              "Genetic_Covariance": pl.Float64,
              "Genetic_Correlation": pl.Float64,
              "Lower_bound_rg": pl.Float64,
              "Upper_bound_rg":pl.Float64,
              "P": pl.Float64}

def regions_metrics(df, total_region):
    """Compute HDL-L region metrics.

    Parameters
    ----------
    df : polars dataframe
        HDL-L result for a single pair.
    total_region : int
        Total number of regions.

    Returns
    -------
    list
        Mean heritability of study 1,
        Mean p-value of heritability of study 1,
        Mean heritability of study 2,
        Mean p-value of heritability of study 2,
        Mean covariance,
        Mean correlation,
        Mean p-value,
        Number of negative regions in results,
        Number of positive regions in results,
        Total number of regions in results,
        Proportion of regions in results.
    """
    # Bound extreme correlations
    corr_col = "Genetic_Correlation"
    df = df.with_columns(
        pl.when(pl.col(corr_col) > 1)
        .then(1)
        .when(pl.col(corr_col) < -1)
        .then(-1)
        .otherwise(pl.col(corr_col))
        .alias(corr_col))

    df = df.drop_nulls()

    # Heritability
    avg_h1 = df.select("Heritability_1").mean().item()
    avg_p_h1 = df.select("P_value_Heritability_1").mean().item()
    avg_h2 = df.select("Heritability_2").mean().item()
    avg_p_h2 = df.select("P_value_Heritability_2").mean().item()

    # Correlation
    avg_cov = df.select("Genetic_Covariance").mean().item()
    avg_corr = df.select(corr_col).mean().item()
    avg_p = df.select("P").mean().item()

    # Regions
    neg_region = df.filter(pl.col(corr_col) < 0).shape[0]
    pos_region = df.filter(pl.col(corr_col) >= 0).shape[0]
    n_region = df.select(pl.count("P")).item()

    prop_region = n_region / total_region

    return [avg_h1, avg_p_h1, avg_h2, avg_p_h2,
            avg_cov, avg_corr, avg_p,
            neg_region, pos_region,
            n_region, prop_region]

def append_results(filename, total_region, output):
    """Append pair results into summary file.

    Parameters
    ----------
    filename : str
        HDL-L results for a single pair path.
    total_region : int
        Total number of regions.
    output : str
        HDL-L summary output path.

    Returns
    -------
    added line in tsv file
        Pair as rows and results as columns:
        STUDY1 (First study),
        STUDY2 (Second study),
        AVG_H1 (Mean heritability of first study),
        AVG_H1_P (Mean p-value of heritability of first study),
        AVG_H2 (Mean heritability of second study),
        AVG_H2_P (Mean p-value of heritability of second study),
        AVG_COV (Mean covariance),
        AVG_CORR (Mean correlation),
        AVG_P (Mean p-value),
        NEG_REGION (Number of negative regions in results),
        POS_REGION (Number of positive regions in results),
        N_REGION (Total number of regions in results),
        PROP_REGION (Proportion of regions in results).
    """
    s1, s2 = filename.split('/')[-1].split('.')[:2]
    results = pl.read_csv(filename, null_values="NA",
                          schema_overrides = HDLL_SCHEMA)

    if len(results) != 0:
        res = regions_metrics(results, total_region)
        with open(output, 'a') as f_out:
            sep = '\t'
            f_out.write(f"{s1}\t{s2}\t{sep.join(map(str, res))}\n")

def summarize_results(filename, total_region, output):
    """Summarize HDL results.

    Parameters
    ----------
    filename : str
        HDL description file path.
    total_region : int
        Total number of regions.
    output : str
        HDL-L summary output path.

    Returns
    -------
    tsv file
        Pairs as rows and results as columns:
        STUDY1 (First study),
        STUDY2 (Second study),
        AVG_H1 (Mean heritability of first study),
        AVG_H1_P (Mean p-value of heritability of first study),
        AVG_H2 (Mean heritability of second study),
        AVG_H2_P (Mean p-value of heritability of second study),
        AVG_COV (Mean covariance),
        AVG_CORR (Mean correlation),
        AVG_P (Mean p-value),
        NEG_REGION (Number of negative regions in results),
        POS_REGION (Number of positive regions in results),
        N_REGION (Total number of regions in results),
        PROP_REGION (Proportion of regions in results).
    """
    description = pl.read_csv(filename,
                              separator=' ',
                              has_header=False,
                              new_columns=["s1", "s2", "output"])

    # Intialize file with header
    with open(output, 'w') as f_out:
        f_out.write(f"{'\t'.join(HDLL_HEADER)}\n")

    # Read results
    for pair in description['output']:
        pair = pair.replace("/HDL/", "/HDL-L/")
        pair = pair.replace(".txt", ".csv")
        print(pair)
        append_results(pair, total_region, output)

if __name__ == "__main__":
    # Parameters
    _, DESCRIPTION, TOTAL_REGION, OUT = sys.argv

    # Method
    hdll_summary = OUT.replace("/HDL/", "/HDL-L/")
    summarize_results(DESCRIPTION, int(TOTAL_REGION), hdll_summary)
