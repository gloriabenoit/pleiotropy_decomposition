"""Summarize HDL-L results."""

import sys

import polars as pl

HDL_SCHEMA = {"Trait1": pl.String,
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
    """Compute region metrics."""
    # Truncate out of bound correlations
    df = df.with_columns(
             pl.when(pl.col("Genetic_Correlation") > 1)
             .then(1)
             .when(pl.col("Genetic_Correlation") < -1)
             .then(-1)
             .otherwise(pl.col("Genetic_Correlation"))
             .alias("Genetic_Correlation")
    )

    df = df.drop_nulls()

    # Heritability
    avg_h1 = df.select("Heritability_1").mean().item()
    avg_p_h1 = df.select("P_value_Heritability_1").mean().item()
    avg_h2 = df.select("Heritability_2").mean().item()
    avg_p_h2 = df.select("P_value_Heritability_2").mean().item()

    # Correlation
    avg_cov = df.select("Genetic_Covariance").mean().item()
    avg_corr = df.select("Genetic_Correlation").mean().item()
    avg_p = df.select("P").mean().item()

    # Regions
    neg_region = df.filter(pl.col("Genetic_Correlation") < 0).shape[0]
    pos_region = df.filter(pl.col("Genetic_Correlation") >= 0).shape[0]
    n_region = df.select(pl.count("P")).item()

    prop_region = n_region / total_region

    res = [avg_h1, avg_p_h1, avg_h2, avg_p_h2,
           avg_cov, avg_corr, avg_p,
           neg_region, pos_region,
           n_region, prop_region]

    return res

def initialize_file(output):
    """Initialize results file."""
    header = ["TRAIT1", "TRAIT2",
              "AVG_H1", "AVG_H1_P", "AVG_H2", "AVG_H2_P",
              "AVG_COV", "AVG_CORR", "AVG_P",
              "NEG_REGION", "POS_REGION",
              "N_REGION", "PROP_REGION"]
    with open(output, 'w') as f_out:
        f_out.write(f"{'\t'.join(header)}\n")

def write_results(filename, total_region, output):
    """Append results into file."""
    t1, t2 = filename.split('/')[-1].split('.')[:2]
    results = pl.read_csv(filename, null_values="NA",
                          schema_overrides = HDL_SCHEMA)

    if len(results) != 0:
        res = regions_metrics(results, total_region)
        with open(output, 'a') as f_out:
            sep = '\t'
            f_out.write(f"{t1}\t{t2}\t{sep.join(map(str, res))}\n")

def summarize_results(reference, data_dir, total_region, output):
    """Summarize results."""
    initialize_file(output)

    for pair in reference['output']:
        t1, t2 = pair.split('.')[:2]
        filename = f"{data_dir}/output/{t1}.{t2}.csv"
        write_results(filename, total_region, output)

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, DESCRIPTION, TOTAL_REGION, OUT = sys.argv
    REFERENCE = pl.read_csv(DESCRIPTION,
                            separator=' ',
                            has_header=False,
                            new_columns=["f1", "f2", "output"])

    # Method
    summarize_results(REFERENCE, DATA_DIR, float(TOTAL_REGION), OUT)
