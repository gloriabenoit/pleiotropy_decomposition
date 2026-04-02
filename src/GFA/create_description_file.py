"""Create a GFA pipeline description file."""

import sys

import polars as pl

def create_description(directory, sample, output):
    """Create GFA description file.
    
    Parameters
    ----------
    directory : str
        JASS cleaned GWAS directory.
    sample : polars dataframe
        Studies as rows and information as columns:
        ID (Study name),
        N (Sample size).
    output : str
        Description output path.

    Returns
    -------
    csv file
        Studies as rows and information as columns:
        name (Study name),
        raw_data_path (Full path to summary statistics),
        pub_sample_size (Sample size),
        effect_is_or (Indicator of if effects are reported as odds ratios),
        chrom (Chromosome column name),
        pos (Position column name),
        snp (rsID column name),
        A1 (Effect allele column name),
        A2 (Other allele column name),
        beta_hat (Effect estimate column name),
        se (Standard error column name),
        p_value (P-value column name),
        sample_size (Sample size column name),
        af (Effect allele frequency column name)
    """
    name = sample["ID"].to_list()
    raw_data_path = [f"{directory}/{study}.txt" for study in name]
    pub_sample_size = sample.get_column("N").cast(pl.Int64).to_list()

    df = pl.DataFrame({'name': name,
                    'raw_data_path': raw_data_path,
                    "pub_sample_size": pub_sample_size,
                    "effect_is_or": "FALSE",
                    "chrom": "chrom",
                    "pos": "pos",
                    "snp": "rsID",
                    "A1": "A0",
                    "A2": "A1",
                    "beta_hat": "Z",
                    "se": "NA",
                    "p_value": "P",
                    "sample_size": "N",
                    "af": "NA",
                    })

    df.write_csv(output)

if __name__ == "__main__":
    # Parameters
    _, REF_DATA_DIR, ALL_SAMPLE, DESCRIPTION = sys.argv
    SAMPLES = pl.read_csv(ALL_SAMPLE)

    # Method
    create_description(REF_DATA_DIR, SAMPLES, DESCRIPTION)
