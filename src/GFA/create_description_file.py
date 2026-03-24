"""Create a GFA pipeline description file."""

import sys

import polars as pl

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def create_description(data_dir, data, output):
    """Create description file."""
    name = data["ID"].to_list()
    raw_data_path = [f"{data_dir}/{pheno}.txt" for pheno in name]
    pub_sample_size = data.get_column("N").cast(pl.Int64).to_list()

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
    _, DATA_DIR, JASS_SAMPLE_PATH, DESCRIPTION = sys.argv
    INFO = pl.read_csv(JASS_SAMPLE_PATH)

    # Method
    create_description(DATA_DIR, INFO, DESCRIPTION)
