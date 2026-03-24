"""Run GUIDE."""

# import importlib.util
import sys

import polars as pl

sys.path.append("./module/GUIDE")
from GUIDE import guide, var_comp

def format_betas(effect):
    """Format betas to match guide input."""
    df = (
        pl.read_csv(effect)
        .drop("rsID")
        )
    return df.to_numpy(), df.columns

def run_guide(effect, L,
              factors_out, loadings_out, variance_out,
              mean_center=True, standardize=False, SE=""):
    """Run GUIDE."""
    betas, phenotypes = format_betas(effect)

    W_XL, W_LT, Sc, mix = guide(betas, L=L,
                                mean_center=mean_center,
                                standardize=standardize)
    var_comp_LT = var_comp(betas, W_XL)

    pheno_names = pl.DataFrame(phenotypes).rename({"column_0": ""})
    factors = pl.concat([pheno_names, pl.DataFrame(W_LT.T)],
                        how="horizontal")
    loadings = pl.DataFrame(W_XL)
    variance = pl.concat([pheno_names, pl.DataFrame(var_comp_LT)],
                         how="horizontal")

    factors.write_csv(factors_out, include_header=False)
    loadings.write_csv(loadings_out, include_header=False)
    variance.write_csv(variance_out, include_header=False)

if __name__ == "__main__":
    # Parameters
    _, EFFECT_OUT, K, FACTORS_OUT, LOADINGS_OUT, VARIANCE_OUT = sys.argv

    # Method
    run_guide(EFFECT_OUT, int(K),
              FACTORS_OUT, LOADINGS_OUT, VARIANCE_OUT,
              standardize=True)
