"""Run GUIDE."""

import sys

import polars as pl

sys.path.append("./module/GUIDE")
from GUIDE import guide, var_comp

def read_effects(filename):
    """Read effects.

    Parameters
    ----------
    filename : str
        Effects path.

    Returns
    -------
    numpy array
        Variants as rows and effects as columns.
    list
        Input studies.
    """
    df = (
        pl.read_csv(filename)
        .drop("rsID")
        )
    return df.to_numpy(), df.columns

def run_guide(effect, k,
              factors_out, loadings_out, variance_out):
    """Run GUIDE.

    Parameters
    ----------
    effect : numpy array
        Variants as rows and effects as columns.
    k : int
        Number of factors to compute.
    factors_out : str
        Study loadings of computed factors output path.
    loadings_out : str
        Variant loadings of computed factors output path.
    variance_out : str
        Variance of computed factors output path.

    Returns
    -------
    csv file
        Study loadings for computed factors.
    csv file
        Variant loadings for computed factors.
    csv file
        Variance of computed factors.
    """
    betas, phenotypes = read_effects(effect)

    W_XL, W_LT, _, _ = guide(betas, L=k,
                                mean_center=True,
                                standardize=True)
    var_comp_LT = var_comp(betas, W_XL)

    pheno_names = pl.DataFrame(phenotypes).rename({"column_0": ""})

    # Study loadings
    factors = pl.concat([pheno_names, pl.DataFrame(W_LT.T)],
                        how="horizontal")
    factors.write_csv(factors_out, include_header=False)

    # Variant loadings
    loadings = pl.DataFrame(W_XL)
    loadings.write_csv(loadings_out, include_header=False)

    # Factor variance
    variance = pl.concat([pheno_names, pl.DataFrame(var_comp_LT)],
                         how="horizontal")
    variance.write_csv(variance_out, include_header=False)

if __name__ == "__main__":
    # Parameters
    _, EFFECT_OUT, K, FACTORS_OUT, LOADINGS_OUT, VARIANCE_OUT = sys.argv

    # Method
    run_guide(EFFECT_OUT, int(K),
              FACTORS_OUT, LOADINGS_OUT, VARIANCE_OUT)
