# 03_PROCESS: Create IDs and save final datasets

process_data <- function(data) {
  library(dplyr)
  library(stringr)

  # Extract data objects
  metadata <- data$metadata_clean

  # Load existing mapping as fallback for missing acronyms
  existing_mapping <- NULL
  if (file.exists("inst/extdata/project_mapping.csv")) {
    existing_mapping <- read.csv("inst/extdata/project_mapping.csv") |>
      mutate(parent_dir = dirname(dirname(document_path))) |>
      select(project_id, parent_dir, project_acronym_fallback = project_acronym)
  }

  # CREATE PROJECT IDENTIFIERS
  # Format: {TYPE}/{ACRONYM}
  create_project_mapping <- function(df, fallback) {
    result <- df |>
      mutate(parent_dir = dirname(dirname(document_path)))

    # Join with fallback if available
    if (!is.null(fallback)) {
      result <- result |>
        left_join(fallback, by = "parent_dir") |>
        mutate(
          project_acronym = ifelse(
            is.na(project_acronym) | project_acronym == "",
            project_acronym_fallback,
            project_acronym
          )
        ) |>
        select(-project_acronym_fallback, -project_id)
    }

    # Check for still-missing acronyms
    missing <- result |> filter(is.na(project_acronym) | project_acronym == "")
    if (nrow(missing) > 0) {
      cat("WARNING: Missing project_acronym for:\n")
      cat(paste(" ", missing$document_path, collapse = "\n"), "\n")
      stop("Cannot proceed without project acronyms")
    }

    result |>
      mutate(
        project_id = paste(toupper(project_category), toupper(project_acronym), sep = "/")
      ) |>
      select(project_id, document_path, project_category, project_acronym, project_title, -parent_dir)
  }

  # Create mapping table
  project_mapping <- create_project_mapping(metadata, existing_mapping)

  # Function to replace document_path with project_id in datasets
  add_project_id <- function(df, mapping) {
    # Extract parent directory path for more robust matching (to handle application vs report subdirs)
    mapping_dirs <- mapping |>
      mutate(parent_dir = dirname(dirname(document_path))) |>
      select(project_id, parent_dir)

    df |>
      mutate(parent_dir = dirname(dirname(document_path))) |>
      left_join(mapping_dirs, by = "parent_dir") |>
      select(-document_path, -parent_dir) |>
      relocate(project_id, .before = everything())
  }

  # Add project_id to all datasets
  metadata_final <- add_project_id(metadata, project_mapping)
  budget_final <- add_project_id(data$budget_long, project_mapping)
  ethics_final <- add_project_id(data$ethics, project_mapping)
  report_metadata_final <- add_project_id(data$report_metadata_clean, project_mapping)
  applicants_final <- add_project_id(data$applicants, project_mapping)
  keywords_final <- add_project_id(data$keywords, project_mapping)
  work_packages_final <- add_project_id(data$work_packages, project_mapping)
  coapplicants_final <- add_project_id(data$coapplicants, project_mapping)
  report_output_final <- add_project_id(data$report_output, project_mapping)

  # SAVE FINAL DATASETS (sorted by project_id)
  write.csv(project_mapping |> arrange(project_id), "inst/extdata/project_mapping.csv", row.names = FALSE)
  write.csv(metadata_final |> arrange(project_id), "inst/extdata/application_metadata.csv", row.names = FALSE)
  write.csv(budget_final |> arrange(project_id), "inst/extdata/application_budget.csv", row.names = FALSE)
  write.csv(ethics_final |> arrange(project_id), "inst/extdata/application_ethics.csv", row.names = FALSE)
  write.csv(report_metadata_final |> arrange(project_id), "inst/extdata/report_metadata.csv", row.names = FALSE)
  write.csv(report_output_final |> arrange(project_id), "inst/extdata/report_output.csv", row.names = FALSE)

  # Save tidy tables with clear naming (sorted by project_id)
  write.csv(applicants_final |> arrange(project_id), "inst/extdata/application_metadata_applicants.csv", row.names = FALSE)
  write.csv(keywords_final |> arrange(project_id), "inst/extdata/application_metadata_keywords.csv", row.names = FALSE)
  write.csv(work_packages_final |> arrange(project_id), "inst/extdata/application_metadata_work_packages.csv", row.names = FALSE)
  write.csv(coapplicants_final |> arrange(project_id), "inst/extdata/report_metadata_coapplicants.csv", row.names = FALSE)

  cat("03_process.R completed successfully\n")
  cat("Created", nrow(project_mapping), "unique project identifiers\n")
  cat("Sample IDs:", head(project_mapping$project_id, 3), "\n")

  # Return final data structure
  return(list(
    project_mapping = project_mapping,
    metadata_final = metadata_final,
    budget_final = budget_final,
    ethics_final = ethics_final,
    report_metadata_final = report_metadata_final,
    applicants_final = applicants_final,
    keywords_final = keywords_final,
    work_packages_final = work_packages_final,
    coapplicants_final = coapplicants_final
  ))
}
