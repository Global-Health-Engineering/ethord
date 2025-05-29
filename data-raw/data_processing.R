# Description ------------------------------------------------------------------
# R script to process uploaded raw data into a tidy, analysis-ready data frame

# Read data --------------------------------------------------------------------
list_of_datasets <- # read all csvs from ./data-raw/

# janitor::clean_names()
# replace null / NA string, with NA value 


# Export Data ------------------------------------------------------------------
usethis::use_data(, overwrite = TRUE)
fs::dir_create(here::here("inst", "extdata"))
readr::write_csv(,
                 here::here("inst", "extdata", paste0("", ".csv")))
