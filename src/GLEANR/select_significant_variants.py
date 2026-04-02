"""Select significant variants."""

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

def get_significant_snp(studies, directory, p_thresh):
    """Keep variants under p-value threshold.

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
    set
        Variants under p-value significance threshold.
    """
    selection = set()

    for filename in studies:
        df = pl.read_csv(f"{directory}/{filename}.txt", separator="\t")
        df = df.filter(pl.col("P") < p_thresh)
        selection.update(set(df.get_column("rsID").to_list()))

    return selection

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
    _, STUDIES_PATH, REF_DATA_DIR, P_THRESH, OUT = sys.argv
    STUDIES = read_list_in_file(STUDIES_PATH)

    # Method
    unique_signif_snps = get_significant_snp(STUDIES, REF_DATA_DIR, float(P_THRESH))
    save_variants(unique_signif_snps, OUT)
