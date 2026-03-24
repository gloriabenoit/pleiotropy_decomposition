library(readr)
library(dplyr)
library(purrr)
library(stringr)
library(GFA)

args = commandArgs(trailingOnly=TRUE)

corr_path <- args[1]
cov_path <- args[2]
zmat_pruned <- args[3]
p_thresh <- as.numeric(args[4])
cond_num <- as.numeric(args[5])
out <- args[6]

corr.mat <- read.table(corr_path, sep=",", header=TRUE, row.names = 1)
cov.mat <- read.table(cov_path, sep=",", header=TRUE, row.names = 1)

# If missing values in the matrices
if (! any(is.na(corr.mat)) || ! any(is.na(cov.mat))) {
    ret <- list(R = data.matrix(cov.mat), Rg = data.matrix(corr.mat), names = rownames(corr.mat))
} else {
    print("Correlation and covariance matrices contain NA values.")
    print("Computing own correlation and covariance matrices.")
    c <- 1:22
    z_files <- sapply(c, function(i) gsub("@", i, zmat_pruned))

    X <- map_dfr(z_files, readRDS)

    ntrait <- X %>%
    select(ends_with(".z")) %>%
    ncol()

    Z_hat <- X %>%
    select(ends_with(".z")) %>%
    as.matrix()

    cond_num <- 1000
    if(!is.finite(cond_num)){
        mwc <- FALSE
    }else{
        mwc <- TRUE
    }

    nms <- colnames(Z_hat) %>% stringr::str_replace(".z$", "")
    Rpt <- R_pt(B_hat = Z_hat,
                S_hat = matrix(1, nrow = nrow(Z_hat), ncol = ncol(Z_hat)),
                p_val_thresh = p_thresh,
                return_cor = TRUE,
                make_well_conditioned = mwc,
                cond_num = cond_num
                )

    ret <- list(R = Rpt, names = nms)
}

saveRDS(ret, file = out)
