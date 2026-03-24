"""Summarize SUPERGNOVA results."""

import sys

import polars as pl

def regions_metrics(df, total_region):
    """Compute region metrics."""
    # Truncate out of bound correlations
    df = df.with_columns(
             pl.when(pl.col("corr") > 1)
             .then(1)
             .when(pl.col("corr") < -1)
             .then(-1)
             .otherwise(pl.col("corr"))
             .alias("corr")
    )

    df = df.drop_nulls()

    # Heritability
    avg_h1 = df.select("h2_1").mean().item()
    avg_h2 = df.select("h2_2").mean().item()

    # Correlation
    avg_cov = df.select("rho").mean().item()
    avg_corr = df.select("corr").mean().item()
    avg_p = df.select("p").mean().item()

    # Regions
    neg_region = df.filter(pl.col("corr") < 0).shape[0]
    pos_region = df.filter(pl.col("corr") >= 0).shape[0]
    n_region = df.select(pl.count("corr")).item()

    prop_region = n_region / total_region

    res = [avg_h1, avg_h2,
           avg_cov, avg_corr, avg_p,
           neg_region, pos_region,
           n_region, prop_region]

    return res

def initialize_file(output):
    """Initialize results file."""
    header = ["TRAIT1", "TRAIT2",
              "AVG_H1", "AVG_H2",
              "AVG_COV", "AVG_CORR", "AVG_P",
              "NEG_REGION", "POS_REGION",
              "N_REGION", "PROP_REGION"]
    with open(output, 'w') as f_out:
        sep = '\t'
        f_out.write(f"{sep.join(header)}\n")

def write_results(filename, total_region, output):
    """Append results into file."""
    t1, t2 = filename.split('/')[-1].split('.')[:2]
    results = pl.read_csv(filename, separator=' ', null_values="NA")

    if len(results) != 0:
        res = regions_metrics(results, total_region)
        with open(output, 'a') as f_out:
            sep = '\t'
            f_out.write(f"{t1}\t{t2}\t{sep.join(map(str, res))}\n")

def summarize_results(reference, data_dir, total_region, output):
    """Summarize results."""
    initialize_file(output)

    for pair in reference['output']:
        filename = f"{data_dir}/output/{pair}"
        write_results(filename, total_region, output)

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, DESCRIPTION, TOTAL_REGION, OUT = sys.argv
    REFERENCE = pl.read_csv(DESCRIPTION,
                            separator=' ',
                            has_header=False,
                            new_columns=["f1", "f2", "n1", "n2", "output"])

    # Method
    summarize_results(REFERENCE, DATA_DIR, float(TOTAL_REGION), OUT)
