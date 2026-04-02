"""Summarize HDL results."""

import sys

import polars as pl

HDL_HEADER = ["STUDY1", "STUDY2",
          "H1", "H1_SE", "H2", "H2_SE",
          "COV", "COV_SE",
          "CORR", "CORR_SE",
          "P"]

def read_metrics(line, se=True):
    """Read metrics from line.

    Parameters
    ----------
    line : str
        Line in HDL results file.
    se : bool
        Whether to read value standard error (Default is True).

    Returns
    -------
    list/tuple/str/float
        Value with or without standard error,
        NA otherwise.
    """
    splitted = line.split()
    # Reading two values
    if se:
        value = splitted[-2]
        se_value = splitted[-1].strip("()")

        if (value == "Inf" or value == "-Inf") and se_value == "NA":
            return ["NA", "NA"]

        return float(value), float(se_value)

    # Reading one value
    value = splitted[-1]
    if value == "NA":
        return value

    return float(value)

def get_metrics(filename):
    """Read HDL results.

    Parameters
    ----------
    filename : str
        HDL results for a single pair path.

    Returns
    -------
    list
        Heritability of phenotype 1 and standard error,
        Heritability of phenotype 2 and standard error,
        Genetic covariance and standard error,
        Genetic correlation and standard error,
        P-value.
    """
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

def append_results(filename, output):
    """Append pair results into summary file.

    Parameters
    ----------
    filename : str
        HDL results for a single pair path.
    output : str
        HDL summary output path.

    Returns
    -------
    tsv file
        Pairs as rows and results as columns:
        STUDY1 (First study),
        STUDY2 (Second study),
        H1 (Heritability of first study),
        H1_SE (Standard error of first study heritability),
        H2 (Heritability of second study),
        H2_SE (Standard error of second study heritability),
        COV (Genetic covariance),
        COV_SE (Standard error of genetic covariance),
        CORR (Genetic correlation),
        CORR_SE (Standard error of genetic correlation),
        P (P-value).
    """
    s1, s2 = filename.split('/')[-1].split('.')[:2]
    res = get_metrics(filename)
    if len(res) != 0:
        with open(output, 'a') as f_out:
            sep = '\t'
            f_out.write(f"{s1}\t{s2}\t{sep.join(map(str, res))}\n")

def summarize_results(filename, output):
    """Summarize HDL results.

    Parameters
    ----------
    filename : str
        HDL description file path.
    output : str
        HDL summary output path.

    Returns
    -------
    tsv file
        Pairs as rows and results as columns:
        STUDY1 (First study),
        STUDY2 (Second study),
        H1 (Heritability of first study),
        H1_SE (Standard error of first study heritability),
        H2 (Heritability of second study),
        H2_SE (Standard error of second study heritability),
        COV (Genetic covariance),
        COV_SE (Standard error of genetic covariance),
        CORR (Genetic correlation),
        CORR_SE (Standard error of genetic correlation),
        P (P-value).
    """
    description = pl.read_csv(filename,
                              separator=' ',
                              has_header=False,
                              new_columns=["s1", "s2", "output"])

    # Intialize file with header
    with open(output, 'w') as f_out:
        sep = '\t'
        f_out.write(f"{sep.join(HDL_HEADER)}\n")

    # Read results
    for pair in description['output']:
        print(pair)
        append_results(pair, output)

if __name__ == "__main__":
    # Parameters
    _, DESCRIPTION, OUT = sys.argv

    # Method
    summarize_results(DESCRIPTION, OUT)
