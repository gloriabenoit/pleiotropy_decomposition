"""Select SNP with possible pleiotropy."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def count_significant_snp(path, files, p_thresh):
    """Get SNP with p-values inferior to threshold."""
    counts = {}

    for filename in files:
        df = pl.read_csv(f"{path}/{filename}.txt", separator="\t")
        df = df.filter(pl.col("P") < p_thresh)
        signif_snp = df.get_column("rsID").to_list()

        for snp in signif_snp:
            if snp in counts:
                counts[snp] += 1
            else:
                counts[snp] = 1

    return counts

def get_pleiotropic_snp(counts, min_study):
    """Get SNP in more than X study."""
    pleiotropy = [k for k, v in counts.items() if v >= min_study]

    return pleiotropy

def save_snp_list(snp_list, out):
    """Save list of SNP in a file."""
    with open(out, 'w') as f_out:
        for snp in snp_list:
            f_out.write(f"{snp}\n")

if __name__ == "__main__":
    # Parameters
    _, DATA_DIR, PHENOTYPES_PATH, P_THRESH, MIN_STUDY, OUT = sys.argv
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)

    # Method
    counts = count_significant_snp(DATA_DIR, PHENOTYPES, float(P_THRESH))
    pleiotropic_snps = get_pleiotropic_snp(counts, int(MIN_STUDY))
    save_snp_list(pleiotropic_snps, OUT)
