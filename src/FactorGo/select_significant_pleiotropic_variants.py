"""Select variants with possible pleiotropy."""

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

def count_significant_variants(studies, directory, p_thresh):
    """Count variants study significance occurrence.

    Parameters
    ----------
    studies : list
        Input studies.
    directory : str
        JASS cleaned GWAS directory.
    p_thresh : float
        P-value significance threshold (under).

    Returns
    -------
    dict
        Selected variants as keys and study significance occurrences as values.
    """
    counts = {}

    for filename in studies:
        df = pl.read_csv(f"{directory}/{filename}.txt", separator="\t")
        df = df.filter(pl.col("P") < p_thresh)
        signif_snp = df.get_column("rsID").to_list()

        for snp in signif_snp:
            if snp in counts:
                counts[snp] += 1
            else:
                counts[snp] = 1

    return counts

def get_pleiotropic_variants(counts, min_studies):
    """Keep variants over studies significance occurrence threshold.
    
    Parameters
    ----------
    counts : dict
        Variants as keys and studies significance occurrences as values.
    min_studies : int
        Studies significance occurrence threshold (over).

    Returns
    -------
    list
        Selected variants.
    """
    pleiotropy = [k for k, v in counts.items() if v >= min_studies]

    return pleiotropy

def save_variants(variants, output):
    """Save variants selection in a file.
    
    Parameters
    ----------
    variants : list
        Selected variants.
    output : str
        Variant selection output path.

    Returns
    -------
    file
        Selected variants.
    
    """
    with open(output, 'w') as f_out:
        for snp in variants:
            f_out.write(f"{snp}\n")

if __name__ == "__main__":
    # Parameters
    _, STUDIES_PATH, REF_DATA_DIR, P_THRESH, MIN_STUDIES, OUT = sys.argv
    STUDIES = read_list_in_file(STUDIES_PATH)

    # Method
    print("Counting variant significance in studies.")
    counts = count_significant_variants(STUDIES, REF_DATA_DIR, float(P_THRESH))

    print("Keeping pleiotropic variants.")
    pleiotropic_snps = get_pleiotropic_variants(counts, int(MIN_STUDIES))

    save_variants(pleiotropic_snps, OUT)
