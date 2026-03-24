args = commandArgs(trailingOnly=TRUE)

out_dir <- args[1]
t1 <- args[2]
t2 <- args[3]
out <- args[4]

file <- paste0(out_dir, "/res_HDLL", t1, "_", t2, ".RData")
load(file)

write.csv(res.HDLL, paste0(out_dir, '/', out), row.names=FALSE)
file.remove(file)
