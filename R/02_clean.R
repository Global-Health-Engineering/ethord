# 02_CLEAN: Targeted fixes only
# Add specific data cleaning rules here

clean_data <- function(data) {
  library(dplyr)
  library(stringr)

  # Extract data objects
  metadata <- data$metadata_clean

  # TARGETED FIXES
  # Add specific fixes below - each fix should be clearly documented

  # Fix 1: Missing project categories based on document path
  metadata_clean <- metadata |>
    mutate(
      # Extract type from path for missing project_category values
      path_type = str_extract(document_path, "(?<=raw/ORD_files/)\\w+"),
      project_category = case_when(
        !is.na(project_category) ~ project_category,
        path_type == "Contribute" ~ "Contribute Projects",
        path_type == "Explore" ~ "Explore Projects",
        path_type == "Establish" ~ "Establish Projects",
        TRUE ~ project_category
      )
    ) |>
    select(-path_type) |>
    # Fix 2: Standardize project category names
    mutate(
      project_category = case_when(
        project_category == "Establish Projects" ~ "Establish",
        project_category == "Contribute Projects" ~ "Contribute",
        project_category == "Explore Projects" ~ "Explore",
        TRUE ~ project_category
      )
    )

  # Fix 2: Add missing project acronyms
  metadata_clean <- metadata_clean |>
    mutate(
      project_acronym = case_when(
        document_path == "raw/ORD_files/Contribute/Leonarski - 2nd call/application/PSI_Leonarski.pdf" ~ "TimeResHDRMX",
        document_path == "raw/ORD_files/Contribute/Rehrauer/application/ETHZ_ Rehrauer.pdf" ~ "NGSDataBooster",
        document_path == "raw/ORD_files/Contribute/Scherrer/application/WSL_Scherrer.pdf" ~ "PhenoMast",
        document_path == "raw/ORD_files/Contribute/Schultheiss/application/EPFL_Schultheiss.pdf" ~ "XYT",
        TRUE ~ project_acronym
      )
    )

  cat("02_clean.R completed successfully\n")

  # Return updated data with cleaned metadata
  return(list(
    metadata_clean = metadata_clean,
    budget_long = data$budget_long,
    ethics = data$ethics,
    report_metadata_clean = data$report_metadata_clean,
    report_output = data$report_output,
    applicants = data$applicants,
    keywords = data$keywords,
    work_packages = data$work_packages,
    coapplicants = data$coapplicants
  ))
}
