"""Summarize HDL results."""

import sys

import polars as pl

def read_metrics(line, se=True):
    """Read metrics from line."""
    splitted = line.split()
    if se:
        value = splitted[-2]
        se_value = splitted[-1].strip("()")

        if (value == "Inf" or value == "-Inf") and se_value == "NA":
            return ["NA", "NA"]

        return float(value), float(se_value)
    value = splitted[-1]
    if value == "NA":
        return value
    return float(value)

def get_metrics(filename):
    """Read HDL results."""
    with open(filename, 'r') as f_in:
        for line in f_in:
            if line.startswith("Heritability of phenotype 1:"):
                h1, h1_se = read_metrics(line)
            elif line.startswith("Heritability of phenotype 2:"):
                h2, h2_se = read_metrics(line)
            elif line.startswith("Genetic Covariance:"):
                cov, cov_se = read_metrics(line)
            elif line.startswith("Genetic Correlation:"):
                corr, corr_se = read_metrics(line)
            elif line.startswith("P:"):
                p = read_metrics(line, se=False)
            elif line.startswith("Algorithm failed to converge"):
                return ["NA"] * 9

    res = [h1, h1_se, h2, h2_se,
           cov, cov_se,
           corr, corr_se,
           p]

    return res

def initialize_file(output):
    """Initialize results file."""
    header = ["TRAIT1", "TRAIT2",
              "H1", "H1_SE", "H2", "H2_SE",
              "COV", "COV_SE",
              "CORR", "CORR_SE",
              "P"]
    with open(output, 'w') as f_out:
        sep = '\t'
        f_out.write(f"{sep.join(header)}\n")

def write_results(filename, output):
    """Append results into file."""
    t1, t2 = filename.split('/')[-1].split('.')[:2]
    res = get_metrics(filename)
    if len(res) != 0:
        with open(output, 'a') as f_out:
            sep = '\t'
            f_out.write(f"{t1}\t{t2}\t{sep.join(map(str, res))}\n")

def summarize_results(reference, data_dir, output):
    """Summarize results."""
    initialize_file(output)

    for pair in reference['output']:
        filename = f"{data_dir}/output/{pair}"
        write_results(filename, output)

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, DESCRIPTION, OUT = sys.argv
    REFERENCE = pl.read_csv(DESCRIPTION,
                            separator=' ',
                            has_header=False,
                            new_columns=["f1", "f2", "output"])

    # Method
    summarize_results(REFERENCE, DATA_DIR, OUT)
