"""Select significant SNPs."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def get_significant_snp(path, traits, p_thresh):
    """Get SNP with p-values inferior to threshold."""
    selection = set()

    for filename in traits:
        df = pl.read_csv(f"{path}/{filename}.txt", separator="\t")
        df = df.filter(pl.col("P") < p_thresh)
        selection.update(set(df.get_column("rsID").to_list()))

    return selection

def save_snp_list(snp_list, output):
    """Save list of SNP in a file."""
    with open(output, 'w') as f_out:
        for snp in snp_list:
            f_out.write(f"{snp}\n")

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, PHENOTYPES_PATH, P_THRESH, OUT = sys.argv
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    # Method
    unique_signif_snps = get_significant_snp(DATA_DIR, PHENOTYPES, float(P_THRESH))
    # unique_signif_snps = get_unique_snp(signif_snps)
    save_snp_list(unique_signif_snps, OUT)
