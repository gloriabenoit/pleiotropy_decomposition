# .libPaths("/pasteur/helix/projects/GGS_WKD/PROJECT_COPD/WKD_Gloria/env/R/gleanr")
library(gleanr)
library(data.table)

args = commandArgs(trailingOnly=TRUE)

effect <- args[1]
se <- args[2]
corr <- args[3]

out <- args[4]
factors_out <- args[5]
loadings_out <- args[6]
variance_out <- args[7]

beta <- fread(effect)
se <- fread(se)
c <- fread(corr)
c[is.na(c)] <- 0
c.mat <- as.matrix(c)

trait_names <- names(beta)[-1]
snp_names <- unlist(beta$SNP)

beta_m <- as.matrix(beta[,-1])
W_s <- 1/as.matrix(se[,-1])

res <- gleanr(beta_m, W_s, snp_names, trait_names, C=c.mat, K="GRID",conv_objective=0.005, verbosity=0, save_out=FALSE)

saveRDS(res, file=out)

write.csv(res$V, factors_out, row.names=trait_names)

write.csv(res$U, loadings_out, row.names=FALSE)

write.csv(res$PVE, variance_out, row.names=FALSE)
