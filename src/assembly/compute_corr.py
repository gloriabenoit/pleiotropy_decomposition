import itertools
import sys

import polars as pl

from scipy.stats import pearsonr
import numpy as np

def format_assembly(filename):
    """Format assembly results."""
    cols_exclude = ["rsid", "chrom", "piece", "pos", "start", "end"]
    df = pl.read_csv(filename).drop(cols_exclude)
    df = df.with_columns([
        pl.col(c).cast(pl.Float64)
        for c in df.columns
    ])

    return df

def compute_correlations(df, filename):
    """Compute correlations for pipeline assembly results."""
    # col_one = []
    # col_two = []
    # corrs = []
    # pvals = []
    # sizes = []
    with open(filename, "w") as csv_out:
        csv_out.write("COL_ONE,COL_TWO,CORR,P,N_snp\n")

    for c1, c2 in itertools.combinations(df.columns, 2):
        print(c1, c2)
        # if c1.endswith(".HDL-L") or c2.endswith(".HDL-L"):
            # continue

        # Correlation
        df_pair = df.select([c1, c2]).drop_nulls()

        if len(df_pair) < 2:
            corr = None
            pval = None
            size = None
            print("No common results found.")
        else:
            corr, pval = pearsonr(df_pair[c1], df_pair[c2])
            size = df_pair.height

            if np.isnan(corr):
                corr = None
                pval = None
                size = None
                print("One set of common results is constant.")
            else:
                print(f"Correlation: {corr:.2e}, Pval: {pval:.2e} (over {size} SNPs)")

        with open(filename, "a") as csv_out:
            csv_out.write(f"{c1},{c2},{corr},{pval},{size}\n")

        # # Saving results
        # col_one.append(c1)
        # col_two.append(c2)
        # corrs.append(corr)
        # pvals.append(pval)
        # sizes.append(size)

    # return pl.from_dict({"COL_ONE": col_one,
    #                     "COL_TWO": col_two,
    #                     "CORR": corrs,
    #                     "P": pvals,
    #                     "N_snp": sizes})

def save_matrix(df, all_col, filename):
    """Save correlation matrix."""
    df_corr = df.select("COL_ONE", "COL_TWO", "CORR")

    # Rebuild matrix
    df_opp = df_corr.rename({"COL_ONE": "COL_TWO", "COL_TWO": "COL_ONE"})
    df_opp = df_opp.select("COL_ONE", "COL_TWO", "CORR")

    df_sym = pl.concat([df_corr, df_opp])

    corr_matrix = df_sym.pivot(
        values="CORR",
        index="COL_ONE",
        on="COL_TWO"
    ).rename({"COL_ONE": ""})

    # Reorder rows and columns
    order_map = {value: idx for idx, value in enumerate(all_col)}
    corr_matrix = corr_matrix.with_columns(
        pl.col("")
        .replace(order_map)
        .cast(pl.Int32)
        .alias("order")
    )
    corr_matrix = corr_matrix.sort("order")
    corr_matrix = corr_matrix.select([""] + all_col)

    # Save
    corr_matrix.write_csv(filename)

if __name__ == "__main__":
    _, FINAL_ASSEMBLY, SUMMARY_OUT, MAT_OUT = sys.argv

    print("format assembly")
    formatted_assembly = format_assembly(FINAL_ASSEMBLY)
    print("compute correlation")
    compute_correlations(formatted_assembly, SUMMARY_OUT)
    print("save corr matrix")
    corr_assembly = pl.read_csv(SUMMARY_OUT)
    
    # cols = ["F1.FactorGo","F2.FactorGo","F3.FactorGo","F4.FactorGo","F5.FactorGo","F6.FactorGo","F7.FactorGo","F8.FactorGo","F9.FactorGo","F10.FactorGo","F11.FactorGo","F12.FactorGo",
    #         "F1.GFA","F2.GFA","F3.GFA","F4.GFA","F5.GFA","F6.GFA","F7.GFA","F8.GFA","F9.GFA","F10.GFA","F11.GFA","F12.GFA","F13.GFA","F14.GFA","F15.GFA",
    #         "F1.GLEANR","F2.GLEANR","F3.GLEANR","F4.GLEANR","F5.GLEANR","F6.GLEANR",
    #         "F1.GUIDE","F2.GUIDE","F3.GUIDE","F4.GUIDE","F5.GUIDE","F6.GUIDE","F7.GUIDE","F8.GUIDE","F9.GUIDE","F10.GUIDE","F11.GUIDE","F12.GUIDE"]
    # save_matrix(corr_assembly, cols, MAT_OUT)
    save_matrix(corr_assembly, formatted_assembly.columns, MAT_OUT)

