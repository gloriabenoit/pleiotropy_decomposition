"""Update BIM file positions with genetic map."""

import sys

import polars as pl
import numpy as np

def interpolate_cm(pos, map_positions, map_cms):
    """Interpolate centimorgan position from genetic map.

    Parameters
    ----------
    pos : int
        Variant position.
    map_positions : numpy array
        All positions in the map.
    map_cms : numpy array
        All centimorgan positions in the map.

    Returns
    -------
    float
        Interpolated centimorgan position.
    """
    # Outside of map
    if pos <= map_positions[0]:
        return map_cms[0]

    if pos >= map_positions[-1]:
        return map_cms[-1]

    # Find position interval
    idx = np.searchsorted(map_positions, pos) - 1
    x1, x2 = map_positions[idx], map_positions[idx + 1]
    y1, y2 = map_cms[idx], map_cms[idx + 1]

    # Linear interpolation
    return y1 + (y2 - y1) * (pos - x1) / (x2 - x1)

def compute_positions(filename, genetic_map, chrom):
    """Compute BIM file positions from genetic map.

    Parameters
    ----------
    filename : str
        BIM file path.
    genetic_map : str
        Genetic map path.
    chrom : int
        Chromosome number.

    Returns
    -------
    tsv file
        BIM file with updated positions.
    """
    # BIM file
    bim = pl.read_csv(filename,
                      separator='\t',
                      has_header=False,
                      new_columns=["chrom", "rsid", "cm",
                                   "pos", "ref", "alt"])

    # Genetic map
    map_data = pl.read_csv(genetic_map,
                           separator=' ', has_header=True,
                           new_columns=["chr", "pos",
                                        "comb", "cms"])
    map_data = map_data.filter(pl.col("chr") == chrom)
    map_pos = map_data['pos'].to_numpy()
    map_cms = map_data['cms'].to_numpy()

    # Interpolate position
    bim = bim.with_columns(
        pl.col("pos").map_elements(
            lambda p: interpolate_cm(p, map_pos, map_cms),
            return_dtype=pl.Float64,
        ).alias("cm")
    )

    # Save
    bim.write_csv(filename, separator="\t", include_header=False)

if __name__ == "__main__":
    # Parameters
    _, BIM, GENETIC_MAP, CHROM = sys.argv

    compute_positions(BIM, GENETIC_MAP, int(CHROM))
