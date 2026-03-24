args = commandArgs(trailingOnly=TRUE)

local_panel_dir <- args[1]
out <- args[2]

load(paste0(local_panel_dir, "HDLL_LOC_snps.RData"))
write.csv(NEWLOC, out, row.names=F, quote=F)
