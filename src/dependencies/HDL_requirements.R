library(remotes)
install_version("dplyr", "1.1.4", repos='http://cran.us.r-project.org')
install.packages(c("data.table", "doSNOW"), repos='http://cran.us.r-project.org')
devtools::install_github("zhenin/HDL/HDL")
