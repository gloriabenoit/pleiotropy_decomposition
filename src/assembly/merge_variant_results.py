"""Merge variant results accross all methods."""

import itertools
import sys

from functools import reduce

import polars as pl

HDL_SCHEMA = {"Trait1": pl.String,
              "Trait2": pl.String,
              "chr": pl.Int64,
              "piece": pl.Int64,
              "eigen_use": pl.Float64,
              "Heritability_1": pl.Float64,
              "P_value_Heritability_1": pl.Float64,
              "Heritability_2": pl.Float64,
              "P_value_Heritability_2": pl.Float64,
              "Genetic_Covariance": pl.Float64,
              "Genetic_Correlation": pl.Float64,
              "Lower_bound_rg": pl.Float64,
              "Upper_bound_rg":pl.Float64,
              "P": pl.Float64}

LOCAL_PARAM = {"SUPERGNOVA": {"separator": " ",
                              "schema": None,
                              "keep_cols": ["chr", "start", "end", "corr"],
                              "merge_on": ["chrom", "start", "end"]
                              },
               "HDL-L": {"separator": ",",
                         "schema": HDL_SCHEMA,
                         "keep_cols": ["chr", "piece", "Genetic_Correlation"],
                         "merge_on": ["chrom", "piece"]
                         }}

FACTORS_PARAM = {"FactorGo": {"sep_in": "\t",
                              "sep_out": "\t",
                              "has_header": False
                              },
                 "GFA": {"sep_in": ",",
                         "sep_out": ",",
                         "has_header": True
                         },
                 "GLEANR": {"sep_in": " ",
                            "sep_out": ",",
                            "has_header": True
                            },
                 "GUIDE": {"sep_in": ",",
                           "sep_out": ",",
                           "has_header": False}}

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

def variants_info(studies, ref_data_dir):
    """List all variants and their positions.

    Parameters
    ----------
    studies : list
        Input studies.
    ref_data_dir : str
        Path to reference data directory.

    Returns
    -------
    polars dataframe
        Variants as rows and variant info as columns:
        rsID, Chromosome, Position.
    """
    df = pl.concat([
                    pl.read_csv(f"{ref_data_dir}/{study}.txt",
                                separator = "\t",
                                columns = [0, 1, 2])
                    for study in studies
                   ],
                   how="vertical").unique().select(["rsID", "chrom", "pos"])

    df = df.sort(["chrom", "pos"])
    df = df.rename({"rsID": "rsid"})

    return df

def join_variants_to_regions(var_info, region_info):
    """Match variant positions to the corresponding regions.

    Parameters
    ----------
    var_info : polars dataframe
        Variants as rows and variant info as columns:
        rsID, Chromosome, Position.
    region_info : polars dataframe
        Regions as rows and region info as columns:
        rsID, Chromosome, Number, Start, End.

    Returns
    -------
    polars dataframe
        Variants as rows and variant info as columns:
        rsID, Chromosome, Position, Region number, Region start, Region end.
    """
    var_mapped = (
        var_info
        .sort(["chrom", "pos"])
        .join_asof(
            region_info.sort(["chrom", "start"]),
            left_on="pos",
            right_on="start",
            by="chrom",
            strategy="backward",
            check_sortedness=False
        )
        .filter(pl.col("pos") < pl.col("end"))
    )

    var_mapped = var_mapped.join(var_info,
                                 on=["rsid", "chrom", "pos"],
                                 how="full",
                                 coalesce=True)

    return var_mapped

def format_local_results(studies, filename, method):
    """Format local correlation method results into one dataframe.

    Parameters
    ----------
    studies : list
        Input studies.
    filename : str
        Method output path.
    method : str
        Method name.

    Returns
    -------
    polars dataframe
        Variants as rows and method results as columns:
        Chromosome, Region number (HDL-L only),
        Region start (SUPERGNOVA only), Region end (SUPERGNOVA only),
        "{Study A}.{Study B}.{Method}" for all possible pairs.
    """
    dfs = []
    merge_on = LOCAL_PARAM[method]["merge_on"]

    for s1, s2 in itertools.combinations(studies, 2):
        combined = f"{s1}.{s2}"
        corr_col = f"{combined}.{method}"

        new_cols = merge_on + [corr_col]
        df = pl.read_csv(filename.replace('@', combined),
                         separator=LOCAL_PARAM[method]["separator"],
                         null_values="NA",
                         schema_overrides=LOCAL_PARAM[method]["schema"],
                         columns=LOCAL_PARAM[method]["keep_cols"],
                         new_columns=new_cols)

        # Bound unexpected correlations
        df = df.with_columns(
            pl.when(pl.col(corr_col) > 1)
            .then(1)
            .when(pl.col(corr_col) < -1)
            .then(-1)
            .otherwise(pl.col(corr_col))
            .alias(corr_col)
            )

        dfs.append(df)

    # Concatenate all results
    total_df = reduce(
        lambda left, right: left.join(right,
                                      on=merge_on,
                                      how="full",
                                      coalesce=True), dfs)

    return total_df

def assemble_local_results(studies, var_mapped, supergnova_out, hdll_out):
    """Combine results for all local correlation methods.

    Parameters
    ----------
    studies : list
        Input studies.
    var_mapped : polars dataframe
        Variants as rows and variant info as columns:
        Chromosome, Position, Region number, Region start, Region end.
    supergnova_out : polars dataframe
        Variants as rows and method results as columns:
        "{Study A}.{Study B}.SUPERGNOVA" for all possible pairs.
    hdll_out : polars dataframe
        Variants as rows and method results as columns:
        "{Study A}.{Study B}.HDL-L" for all possible pairs.

    Returns
    -------
    polars dataframe
        Variants as rows and method results as columns:
        rsID, Chromosome, Position, Region number, Region start, Region end,
        "{Study A}.{Study B}.SUPERGNOVA",
        "{Study A}.{Study B}.HDL-L" for all possible pairs.
    """
    supergnova = format_local_results(studies, supergnova_out, "SUPERGNOVA")
    hdll = format_local_results(studies, hdll_out, "HDL-L")

    # Join results
    local_res = var_mapped.join(supergnova, on=["chrom", "start", "end"],
                                how="full", coalesce=True)
    local_res = local_res.join(hdll, on=["chrom", "piece"],
                               how="full", coalesce=True)

    return local_res

def format_factor_results(results, variants, method, variants_header=False):
    """Format latent factor analysis method results into one dataframe.

    Parameters
    ----------
    results : str
        Method output path (Variant loadings).
    variants : str
        Input variants path.
    method : str
        Method name.
    variants_header : bool
        If input variants file has a header (default is False).

    Returns
    -------
    polars dataframe
        Variants as rows and method results as columns:
        rsID,
        "F{i}.{Method}" for all factors found.
    """
    # Input variants
    var = pl.read_csv(variants,
                           separator=FACTORS_PARAM[method]["sep_in"],
                           columns=0,
                           has_header=variants_header,
                           new_columns=["rsid"])

    # Results
    res = pl.read_csv(results,
                     separator=FACTORS_PARAM[method]["sep_out"],
                     has_header=FACTORS_PARAM[method]["has_header"])
    rename_dict = dict(zip(res.columns, [f"F{i+1}.{method}" for i in range(len(res.columns))]))
    res = res.rename(rename_dict)

    # Add variant information to results
    factor_out = pl.concat([var, res], how="horizontal")

    return factor_out

def assemble_factor_results(fgo_res, gfa_res, gleanr_res, guide_res,
                            fgo_snp="", gfa_snp="", gleanr_snp="", guide_snp="",
                            variants=""):
    """Combine results for all latent factor analysis methods.

    Parameters
    ----------
    fgo_res : str
        FactorGo output path (Variant loadings).
    gfa_res : str
        GFA output path (Variant loadings).
    gleanr_res : str
        GLEANR output path (Variant loadings).
    guide_res : str
        GUIDE output path (Variant loadings).
    fgo_snp : str
        FactorGo input variants path.
    gfa_snp : str
        GFA input variants path.
    gleanr_snp : str
        GLEANR input variants path.
    guide_snp : str
        GUIDE input variants path.
    variants : str
        Common input variants path (default is empty).

    Returns
    -------
    polars dataframe
        Variants as rows and method results as columns:
        rsID,
        "F{i}.FactorGo",
        "F{i}.GFA",
        "F{i}.GLEANR",
        "F{i}.GUIDE" for all factors found.
    """
    # Combine variant rsID to results
    if variants:
        fgo = format_factor_results(fgo_res, variants,
                                    "FactorGo")
        gfa = format_factor_results(gfa_res, variants,
                                    "GFA")
        gleanr = format_factor_results(gleanr_res, variants,
                                       "GLEANR")
        guide = format_factor_results(guide_res, variants,
                                      "GUIDE")
    else:
        fgo = format_factor_results(fgo_res, fgo_snp,
                                    "FactorGo", variants_header=True)
        gfa = format_factor_results(gfa_res, gfa_snp,
                                    "GFA")
        gleanr = format_factor_results(gleanr_res, gleanr_snp,
                                       "GLEANR", variants_header=True)
        guide = format_factor_results(guide_res, guide_snp,
                                      "GUIDE", variants_header=True)

    # Join
    factor_res = (fgo
                  .join(gfa, on="rsid", how="full", coalesce=True)
                  .join(gleanr, on="rsid", how="full", coalesce=True)
                  .join(guide, on="rsid", how="left", coalesce=True)
                  )

    return factor_res

def assemble_all_results(local_res, factor_res, output):
    """Combine results for all latent factor analysis methods.

    Parameters
    ----------
    local_res : polars dataframe
        Variants as rows and method results as columns:
        "{Study A}.{Study B}.SUPERGNOVA",
        "{Study A}.{Study B}.HDL-L" for all possible pairs.
    factor_res : polars dataframe
        Variants as rows and method results as columns:
        rsID,
        "F{i}.FactorGo",
        "F{i}.GFA",
        "F{i}.GLEANR",
        "F{i}.GUIDE" for all factors found.
    output : str
        Final assembly output path.

    Returns
    -------
    csv file
        Final assembly with variants as rows and method results as columns:
        rsID, Chromosome, Position, Region number, Region start, Region end,
        "{Study A}.{Study B}.SUPERGNOVA",
        "{Study A}.{Study B}.HDL-L" for all possible pairs,
        "F{i}.FactorGo",
        "F{i}.GFA",
        "F{i}.GLEANR",
        "F{i}.GUIDE" for all factors found.
    """
    final_merge = local_res.join(factor_res, on="rsid", how="right", coalesce=True)
    final_merge = final_merge.select(pl.col("rsid"), pl.all().exclude("rsid"))
    final_merge = final_merge.sort(["chrom", "pos", "piece"])
    final_merge.write_csv(output)

if __name__ == "__main__":
    _, STUDIES_PATH, REF_DATA_DIR, REGIONS = sys.argv[:4]
    SUPERGNOVA_OUT, HDLL_OUT = sys.argv[4:6]
    FACTORGO_OUT, FACTORGO_SNPS = sys.argv[6:8]
    GFA_OUT, GFA_SNPS = sys.argv[8:10]
    GLEANR_OUT, GLEANR_SNPS = sys.argv[10:12]
    GUIDE_OUT, GUIDE_SNPS = sys.argv[12:14]
    FINAL_ASSEMBLY = sys.argv[14]
    USE_FILTERS = sys.argv[15]
    if USE_FILTERS == "false":
        USE_FILTERS = False
        SNP_LIST = sys.argv[16]
    else:
        USE_FILTERS = True
        SNP_LIST = ""

    # Information
    print("Reading studies and variants information.")
    STUDIES = read_list_in_file(STUDIES_PATH)
    var_info = variants_info(STUDIES, REF_DATA_DIR)
    region_info = pl.read_csv(REGIONS,
                              columns = ["CHR", "piece",
                                         "START", "STOP"],
                              new_columns=["chrom", "piece",
                                           "start", "end"])
    var_mapped = join_variants_to_regions(var_info, region_info)

    # Local genetic correlation results
    print("Assembling local genetic correlation methods results.")
    local_res = assemble_local_results(STUDIES, var_mapped, SUPERGNOVA_OUT, HDLL_OUT)

    # Latent factor analysis results
    print("Assembling latent factor analysis methods results.")
    if USE_FILTERS:
        factor_res = assemble_factor_results(FACTORGO_OUT, GFA_OUT, GLEANR_OUT, GUIDE_OUT,
                                             fgo_snp=FACTORGO_SNPS, gfa_snp=GFA_SNPS,
                                             gleanr_snp=GLEANR_SNPS, guide_snp=GUIDE_SNPS)
    else:
        factor_res = assemble_factor_results(FACTORGO_OUT, GFA_OUT, GLEANR_OUT, GUIDE_OUT,
                                             variants=SNP_LIST)

    # Final file
    print("Assembling all results into a single file.")
    assemble_all_results(local_res, factor_res, FINAL_ASSEMBLY)
