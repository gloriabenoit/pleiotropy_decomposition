"""Create a SUPERGNOVA pipeline description file."""

import itertools
import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def get_size(df, phenotype):
    """Read GWAS sample size."""
    pheno_info = df.filter(pl.col("ID") == phenotype)
    size = pheno_info.item(0, "N")
    return int(size)

def create_description(phenotypes, data, output):
    """Create description file."""
    # Per pair
    with open(output, 'w') as description:
        for f1, f2 in itertools.combinations(phenotypes, 2):
            n1, n2 = get_size(data, f1), get_size(data, f2)
            out = f"{f1}.{f2}.txt"
            description.write(f"{f1} {f2} {n1} {n2} {out}\n")

if __name__ == "__main__":
    # Parameters
    _, PHENOTYPES_PATH, SAMPLE_FILE, DESCRIPTION = sys.argv
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)
    INFO = pl.read_csv(SAMPLE_FILE)

    # Method
    create_description(PHENOTYPES, INFO, DESCRIPTION)
