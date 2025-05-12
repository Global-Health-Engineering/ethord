# Description ------------------------------------------------------------------
# R script to process uploaded raw data into a tidy, analysis-ready data frame
# Load packages ----------------------------------------------------------------
## Run the following code in console if you don't have the packages
## install.packages(c("usethis", "fs", "here", "readr", "readxl", "openxlsx"))
library(usethis)
library(fs)
library(here)
library(readr)
library(readxl)
library(openxlsx)

# Read data --------------------------------------------------------------------
ethord <- readr::read_csv("data-raw/data.csv") |>
  janitor::clean_names()
# codebook <- readxl::read_excel("data-raw/codebook.xlsx") |>
#  clean_names()

# Tidy data --------------------------------------------------------------------
## Clean the raw data into a tidy format here


# Export Data ------------------------------------------------------------------
usethis::use_data(ethord, overwrite = TRUE)
fs::dir_create(here::here("inst", "extdata"))
readr::write_csv(ethord,
                 here::here("inst", "extdata", paste0("ethord", ".csv")))
openxlsx::write.xlsx(ethord,
                     here::here("inst", "extdata", paste0("ethord", ".xlsx")))
