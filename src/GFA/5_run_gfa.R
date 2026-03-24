library(dplyr)
library(purrr)
library(stringr)
library(GFA)

args = commandArgs(trailingOnly=TRUE)

R_est_file <- args[1]
zmat_combined <- args[2]
seed <- args[3]
out <- args[4]
factors_out <- args[5]
loadings_out <- args[6]
variance_out <- args[7]

params_file <- "default"
max_snp <- as.numeric("Inf")

chrom <- 1:22
z_files <- mapply(gsub, "@", chrom, zmat_combined)

set.seed(seed)

if(params_file == "default"){
  params <- gfa_default_parameters()
}else{
  params <- readRDS(params_file)
}

# Read in data
X <- map_dfr(z_files, readRDS)

ntrait <- X %>%
          select(ends_with(".z")) %>%
          ncol()

if(nrow(X) > max_snp){
    ix <- sample(seq(nrow(X)), size = max_snp, replace = FALSE)
    X <- X[ix,]
}

Z_hat <- X %>%
         select(ends_with(".z")) %>%
         as.matrix()

SS <- X %>%
      select(ends_with(".ss")) %>%
      as.matrix()

snps <- X$snp

nms <- names(X)[grep(".z$", names(X))] %>% str_replace(".z$", "")

R <- readRDS(R_est_file)

stopifnot(all(R$names %in% nms))
z_order <- match(R$names, nms)
SS <- SS[,z_order]
Z_hat <- Z_hat[,z_order]

rownames(R$R) <- colnames(R$R) <- NULL

N <- apply(SS, 2, median)
t <- system.time(f <- gfa_fit(Z_hat = Z_hat,
                                N = N,
                                R = R$R,
                                params = params))

f$snps <- snps
f$names <- R$names
f$time <- t
saveRDS(f, file=out)

write.csv(f$F_hat, factors_out)
write.csv(f$L_hat, loadings_out, row.names=FALSE)
write.csv(f$gfa_pve$pve, variance_out, row.names=f$names)
