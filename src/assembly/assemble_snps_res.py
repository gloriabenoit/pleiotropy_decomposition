"""Merge results from all methods at the SNP-level"""

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

def read_phenotypes(filename):
    """Read list of phenotypes."""
    with open(filename, 'r') as phenotypes:
        return [line.strip() for line in phenotypes]

def variants_info(phenotypes, ref_data_dir):
    """List all variants and their positions."""
    df = pl.concat([
                    pl.read_csv(f"{ref_data_dir}/{pheno}.txt", separator="\t", columns=[0, 1, 2])
                    for pheno in phenotypes
                   ],how="vertical").unique().select(["rsID", "chrom", "pos"])

    df = df.sort(["chrom", "pos"])
    df = df.rename({"rsID": "rsid"})

    return df

def join_variants_to_regions(var_info, region_info):
    """Match variant positions to the corresponding regions."""
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

def format_local_results(phenotypes, filename, software):
    """Save"""
    dfs = []
    merge_on = LOCAL_PARAM[software]["merge_on"]

    for t1, t2 in itertools.combinations(phenotypes, 2):
        combined = f"{t1}.{t2}"
        new_cols = merge_on + [f"{combined}.{software}"]
        df = pl.read_csv(filename.replace('@', combined),
                         separator=LOCAL_PARAM[software]["separator"],
                         null_values="NA",
                         schema_overrides=LOCAL_PARAM[software]["schema"],
                         columns=LOCAL_PARAM[software]["keep_cols"],
                         new_columns=new_cols)
        dfs.append(df)
    total_df = reduce(
        lambda left, right: left.join(right,
                                      on=merge_on,
                                      how="full",
                                      coalesce=True), dfs)
    return total_df

def assemble_local_results(phenotypes, var_mapped, supergnova_out, hdll_out):
    """Combine local results from SUPERGNOVA and HDL-L"""
    # Read
    supergnova = format_local_results(phenotypes, supergnova_out, "SUPERGNOVA")
    hdll = format_local_results(phenotypes, hdll_out, "HDL-L")

    # Join
    local_res = var_mapped.join(supergnova, on=["chrom", "start", "end"],
                                how="full", coalesce=True)
    local_res = var_mapped.join(hdll, on=["chrom", "piece"],
                               how="full", coalesce=True)

    return local_res

def format_factor_results(res_path, snp_in, software, snp_header=True):
    """Save"""
    # Input SNPs
    snp_list = pl.read_csv(snp_in,
                           separator=FACTORS_PARAM[software]["sep_in"],
                           columns=0,
                           has_header=snp_header,
                           new_columns=["rsid"])

    # Results
    res = pl.read_csv(res_path,
                     separator=FACTORS_PARAM[software]["sep_out"],
                     has_header=FACTORS_PARAM[software]["has_header"])
    rename_dict = dict(zip(res.columns, [f"F{i+1}.{software}" for i in range(len(res.columns))]))
    res = res.rename(rename_dict)

    # Combine SNPs and results
    factor_out = pl.concat([snp_list, res], how="horizontal")

    return factor_out

def assemble_factor_results(fgo_res, gfa_res, gleanr_res, guide_res,
                            fgo_snp="", gfa_snp="", gleanr_snp="", guide_snp="",
                            snp_list=""):
    """Save"""
    # Read
    if snp_list:
        fgo = format_factor_results(fgo_res, snp_list, "FactorGo", snp_header=False)
        gfa = format_factor_results(gfa_res, snp_list, "GFA", snp_header=False)
        gleanr = format_factor_results(gleanr_res, snp_list, "GLEANR", snp_header=False)
        guide = format_factor_results(guide_res, snp_list, "GUIDE", snp_header=False)
    else:
        fgo = format_factor_results(fgo_res, fgo_snp, "FactorGo")
        gfa = format_factor_results(gfa_res, gfa_snp, "GFA", snp_header=False)
        gleanr = format_factor_results(gleanr_res, gleanr_snp, "GLEANR")
        guide = format_factor_results(guide_res, guide_snp, "GUIDE")

    # Join
    factor_res = (fgo
                  .join(gfa, on="rsid", how="full", coalesce=True)
                  .join(gleanr, on="rsid", how="full", coalesce=True)
                  .join(guide, on="rsid", how="left", coalesce=True)
                  )

    return factor_res

def assemble_all_results(local_res, factor_res, final_assembly):
    """save"""
    final_merge = local_res.join(factor_res, on="rsid", how="right", coalesce=True)
    final_merge = final_merge.select(pl.col("rsid"), pl.all().exclude("rsid"))
    final_merge = final_merge.sort(["chrom", "pos", "piece"])
    final_merge.write_csv(final_assembly)

if __name__ == "__main__":
    _, PHENOTYPES_PATH, REF_DATA_DIR, REGIONS_PATH = sys.argv[:4]
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
    PHENOTYPES = read_phenotypes(PHENOTYPES_PATH)
    var_info = variants_info(PHENOTYPES, REF_DATA_DIR)
    region_info = pl.read_csv(REGIONS_PATH,
                              columns = ["CHR", "piece",
                                         "START", "STOP"],
                              new_columns=["chrom", "piece",
                                           "start", "end"])
    var_mapped = join_variants_to_regions(var_info, region_info)

    # Local genetic correlation results
    local_res = assemble_local_results(PHENOTYPES, var_mapped, SUPERGNOVA_OUT, HDLL_OUT)

    # Latent factor analysis results
    if USE_FILTERS:
        factor_res = assemble_factor_results(FACTORGO_OUT, GFA_OUT, GLEANR_OUT, GUIDE_OUT,
                                             fgo_snp=FACTORGO_SNPS, gfa_snp=GFA_SNPS,
                                             gleanr_snp=GLEANR_SNPS, guide_snp=GUIDE_SNPS)
    else:
        factor_res = assemble_factor_results(FACTORGO_OUT, GFA_OUT, GLEANR_OUT, GUIDE_OUT,
                                             snp_list=SNP_LIST)

    # Final file
    assemble_all_results(local_res, factor_res, FINAL_ASSEMBLY)
