"""Get positions from other bim file."""

import sys

import polars as pl
import numpy as np

def interpolate_cm(pos, map_positions, map_cms):
    # before the first map position
    if pos <= map_positions[0]:
        return map_cms[0]
    # after the last map position
    if pos >= map_positions[-1]:
        return map_cms[-1]
    # find interval
    idx = np.searchsorted(map_positions, pos) - 1
    x1, x2 = map_positions[idx], map_positions[idx + 1]
    y1, y2 = map_cms[idx], map_cms[idx + 1]
    # linear interpolation
    return y1 + (y2 - y1) * (pos - x1) / (x2 - x1)

def prepare_data(filename, reference, chrom):
    """Add positions to bim file from reference."""
    bim = pl.read_csv(filename,
                      separator='\t',
                      has_header=False,
                      new_columns=["chrom", "rsid", "cm",
                                   "pos", "ref", "alt"])
    map_data = pl.read_csv(reference,
                           separator=' ', has_header=True,
                           new_columns=["chr", "pos",
                                        "comb", "cms"])

    map_data = map_data.filter(pl.col("chr") == chrom)

    map_pos = map_data['pos'].to_numpy()
    map_cms = map_data['cms'].to_numpy()

    return bim, map_pos, map_cms

def compute_pos(filename, reference, chrom):
    bim, map_pos, map_cms = prepare_data(filename, reference, chrom)

    bim = bim.with_columns(
        pl.col("pos").map_elements(
            lambda p: interpolate_cm(p, map_pos, map_cms),
            return_dtype=pl.Float64,
        ).alias("cm")
    )
    bim.write_csv(filename, separator="\t", include_header=False)

if __name__ == "__main__":
    # Parameters
    _, FILENAME, REFERENCE, CHROM = sys.argv

    compute_pos(FILENAME, REFERENCE, int(CHROM))
