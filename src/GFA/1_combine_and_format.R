library(VariantAnnotation)
library(gwasvcf)
library(dplyr)
library(rlang)
library(readr)
library(purrr)
library(stringr)

require(GFA)

format_flat_chrom <- function(file, chrom, af_thresh,
                              snp_name,
                              pos_name,
                              chrom_name,
                              A1_name, A2_name,
                              beta_hat_name,
                              se_name,
                              p_value_name,
                              af_name,
                              sample_size_name,
                              effect_is_or
                              ){

    if(!se_name %in% c("", "NA", NA)){
        sestring <- paste0(", `", se_name, "`='d'")
    } else {
        sestring <- ""
        se_name <- NA
    }
    if(!p_value_name %in% c("", "NA", NA)){
        pstring <- paste0(", `", p_value_name, "`='d'")
    }else{
        pstring <- ""
        p_value_name <- NA
    }
    if(!sample_size_name %in% c("", "NA", NA)){
        sstring <- paste0(", `", sample_size_name, "`='d'")
    }else{
        sstring <- ""
        sample_size_name <- NA
    }
    if(!pos_name %in% c("", "NA", NA)){
        posstring <- paste0(", `", pos_name, "`='d'")
    }else{
        posstring <- ""
        pos_name <- NA
    }
    if(!af_name %in% c("", "NA", NA)){
        afstring <- paste0(", `", af_name, "`='d'")
    }else{
        afstring <- ""
        af_name <- NA
    }

    col_string <- paste0("cols_only(`", snp_name, "`='c', `",
                     A1_name , "`='c', `", A2_name, "`='c', `",
                     beta_hat_name , "`='d'", sestring, ", `",
                     chrom_name, "`='c'", posstring,
                     pstring,  sstring, afstring, ")")

    h <- read_tsv(pipe(paste0("head -2 ", file)))
    n <- which(names(h) == chrom_name)
    awk_cmd <- paste0("awk -F\"\\t\" '{if ($", n, " == \"", chrom, "\") print $0}' ", file)

    X <- read_tsv(pipe(awk_cmd), col_types = eval(parse(text = col_string)), col_names = names(h))

    # Rename here so theres no problem with A0 and A1 nomenclature
    X <- X %>% rename(A2 = !!A2_name)
    A2_name <- "A2"
    X <- X %>% rename(A1 = !!A1_name)
    A1_name <- "A1"

    if(is.na(se_name)){
        X$se <- 1
        se_name <- "se"
    }

    if(!is.na(af_name)){
        if(!all(is.na(X[[af_name]]))){
          ix <- which(X[[af_name]] > af_thresh & X[[af_name]] < (1-af_thresh))
          X <- X[ix,]
        }
    }

    if(effect_is_or){
        X$beta <- log(X[[beta_hat_name]])
        beta_hat <- "beta"
    }

    dat <- gwas_format(X, snp_name, beta_hat_name, se_name,
                       A1 = A1_name,
                       A2 = A2_name,
                       chrom = chrom_name,
                       pos = pos_name,
                       p_value = p_value_name,
                       sample_size = sample_size_name,
                       allele_freq = af_name,
                       compute_pval = TRUE)

    return(dat)
}

args = commandArgs(trailingOnly=TRUE)

description <- args[1]
sample_size_tol <- args[2]
zmat_combined <- args[3]

info <- read_csv(description)

af_thresh <- 0
for (c in 1:22) {
    out <- gsub("@", c, zmat_combined)
    fulldat <- map(seq(nrow(info)),   function(i){
                            f <- info$raw_data_path[i]
                            dat <- format_flat_chrom(f, c, af_thresh,
                                                        info$snp[i],
                                                        info$pos[i],
                                                        info$chrom[i],
                                                        info$A1[i],
                                                        info$A2[i],
                                                        info$beta_hat[i],
                                                        info$se[i],
                                                        info$p_value[i],
                                                        info$af[i],
                                                        info$sample_size[i],
                                                        as.logical(info$effect_is_or[i]))

                            if(all(is.na(dat$sample_size))){
                            dat$sample_size <- info$pub_sample_size[i]
                            }

                            if(is.finite(sample_size_tol)){
                            m <- median(dat$sample_size)
                            dat <- filter(dat, sample_size > (1-sample_size_tol)*m & sample_size < (1 + sample_size_tol)*m)
                            }
                            n <- info$name[i]
                            se_name <- as_name(paste0(n, ".se"))
                            z_name <- as_name(paste0(n, ".z"))
                            ss_name <- as_name(paste0(n, ".ss"))
                            af_name <- as_name(paste0(n, ".af"))

                            dat$sample_size[is.na(dat$sample_size)] <- as.numeric(info$pub_sample_size)
                            dat <-dat %>%  dplyr::mutate(Z = beta_hat/se) %>%
                                dplyr::rename(REF = A2, ALT = A1) %>%
                                dplyr::select(chrom, snp, REF, ALT,
                                                !!z_name := Z,
                                                !!se_name := se,
                                                !!ss_name := sample_size,
                                                !!af_name := allele_freq)
                    }) %>%
        purrr::reduce(full_join, by = c("chrom", "snp", "REF", "ALT"))

    dup_snps <- fulldat$snp[duplicated(fulldat$snp)]
    if(length(dup_snps) > 0){
        fulldat <- filter(fulldat, !snp %in% dup_snps)
    }

    # Table of how traits are missing each SNP for LD clumping
    miss <- fulldat %>%
            dplyr::select(ends_with(".z")) %>%
            is.na(.) %>%
            rowSums(.)

    ix <- which(miss == 0)

    saveRDS(fulldat[ix,], file=out)
}
