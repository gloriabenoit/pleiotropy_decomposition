library(dplyr)
library(ieugwasr)

args = commandArgs(trailingOnly=TRUE)

zmat_combined <- args[1]
snp_list <- args[2]
zmat_pruned <- args[3]

for (c in 1:22) {
  zmat <- gsub("@", c, zmat_combined)
  X <- readRDS(zmat)
  out <- gsub("@", c, zmat_pruned)

  Z_hat <- X %>%
    select(ends_with(".z")) %>%
    as.matrix()

  dat_clump <- read.table(snp_list, header=F, col.names=c("rsid"))

  ix <- which(X$snp %in% dat_clump$rsid)
  X <- X[ix,]

  saveRDS(X, file=out)
}
