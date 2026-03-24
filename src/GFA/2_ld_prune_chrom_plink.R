library(dplyr)
library(ieugwasr)

args = commandArgs(trailingOnly=TRUE)

ref_path <- args[1]
zmat_combined <- args[2]
r2_thresh <- as.numeric(args[3])
clump_kb <- as.numeric(args[4])
p_thresh <- as.numeric(args[5])
ld_prioritization <- args[6]
zmat_pruned <- args[7]
snp_list <- args[8]

snps <- c()

if(!ld_prioritization %in% c("pvalue", "rank")){
  stop("Unknown prioritization option.\n")
}

for (c in 1:22) {
  zmat <- gsub("@", c, zmat_combined)
  X <- readRDS(zmat)
  out <- gsub("@", c, zmat_pruned)

  Z_hat <- X %>%
    select(ends_with(".z")) %>%
    as.matrix()

  if(ld_prioritization == "pvalue"){
    zmax <- apply(abs(Z_hat), 1, function(x){max(x, na.rm=T)})
    myp <- 2*pnorm(-abs(zmax))

  }else if(ld_prioritization == "rank"){
    Z_rank <- apply(Z_hat,2,function(x){rank(x,na.last = "keep")})
    min_rank <- apply(Z_rank, 1, function(x){min(x, na.rm = T)})
    myp <- min_rank/max(min_rank)

  }

  dat <- data.frame(rsid = X$snp, pval = myp)

  dat_clump <- ld_clump(dat = dat,
                      clump_r2 = r2_thresh,
                      clump_kb = clump_kb,
                      clump_p = p_thresh,
                      plink_bin = genetics.binaRies::get_plink_binary(),
                      bfile = ref_path)

  ix <- which(X$snp %in% dat_clump$rsid)
  X <- X[ix,]

  snps <- c(snps, X$snp)

  saveRDS(X, file=out)
}

write.table(snps, file=snp_list, quote=F, row.names=F, col.names=F)