# 02_CLEAN: Targeted fixes only
# Add specific data cleaning rules here

clean_data <- function(data) {
  library(dplyr)
  library(stringr)
  library(lubridate)
  library(purrr)

  # Extract data objects
  metadata <- data$metadata_clean
  report_metadata <- data$report_metadata_clean
  budget <- data$budget_long
  ethics <- data$ethics

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

  # Fix 3: Clean date formats in report_metadata using helper function
  parse_date_range <- function(date_str) {
    if (is.na(date_str) || date_str %in% c("INSUFFICIENT DATA", "")) {
      return(NA_character_)
    }

    # Handle specific edge cases first
    specific_fixes <- list(
      "Start: 1 Jul 2022; End: 31 Jan 2023 (extended to 31 May 2023)" = "2022-07-01/2023-05-31",
      "March → October 2023" = "2023-03-01/2023-10-31",
      "01.09.2023-28.02.2025" = "2023-09-01/2025-02-28",
      "1.4.2023-31.3.2026" = "2023-04-01/2026-03-31",
      "1.4.2023-30.4.2024" = "2023-04-01/2024-04-30",
      "09.24 to 05.25" = "2024-09-01/2025-05-31",
      "09.24 to 06.25" = "2024-09-01/2025-06-30",
      "08.24 to 07.25" = "2024-08-01/2025-07-31",
      "from 09/24 to 05/25" = "2024-09-01/2025-05-31",
      "01.10.2024-30.06.2025" = "2024-10-01/2025-06-30",
      "09/2024 - 07/2025" = "2024-09-01/2025-07-31",
      "April 2024 – March 2025" = "2024-04-01/2025-03-31",
      "November 1, 2023 – June 31, 2024" = "2023-11-01/2024-06-30",
      "01.05.23 to 31.07.24 (incl. 3 month no-cost extension)" = "2023-05-01/2024-07-31",
      "1st Jan 2024-31st December 2024" = "2024-01-01/2024-12-31",
      "January 1st, 2023 – September 30th, 2023" = "2023-01-01/2023-09-30",
      "June 2023 – May 31 2024" = "2023-06-01/2024-05-31",
      "September 2023 – June 2024" = "2023-09-01/2024-06-30",
      "01.08.2024 - 28.02.2026 (18 m)" = "2024-08-01/2026-02-28",
      "2023-05-01 – 2024-07-31" = "2023-05-01/2024-07-31",
      "1. Sept 2024 & 28. Feb 2026" = "2024-09-01/2026-02-28",
      "start: 01.09.2024, end: 28.02.2026" = "2024-09-01/2026-02-28",
      "01.10.2024-31.03.2026" = "2024-10-01/2026-03-31",
      "2024-11-02 to 2024-11-03" = "2024-11-02/2024-11-03",
      "01.01.2024 – 31.09.2024" = "2024-01-01/2024-09-30",
      "2022-09-01 – 2023-04-30" = "2022-09-01/2023-04-30"
    )

    if (date_str %in% names(specific_fixes)) {
      return(specific_fixes[[date_str]])
    }

    # Year only format
    if (str_detect(date_str, "^\\d{4}$")) {
      return(paste0(date_str, "-01-01/", date_str, "-12-31"))
    }

    # Try to split on common separators and parse
    if (str_detect(date_str, " – ")) {
      parts <- str_split(date_str, " – ")[[1]]
      start_date <- dmy(parts[1])
      end_date <- dmy(parts[2])
      if (!is.na(start_date) && !is.na(end_date)) {
        return(paste0(start_date, "/", end_date))
      }
    }

    if (str_detect(date_str, " to ")) {
      parts <- str_split(date_str, " to ")[[1]]
      # Try dd.mm.yy format first
      start_date <- dmy(parts[1])
      end_date <- dmy(parts[2])
      if (!is.na(start_date) && !is.na(end_date)) {
        return(paste0(start_date, "/", end_date))
      }

      # Try mm/yy format
      if (str_detect(parts[1], "^\\d{2}/\\d{2}$")) {
        start_date <- dmy(paste0("01/", parts[1]))
        end_date <- dmy(paste0("01/", parts[2])) + months(1) - days(1)
        if (!is.na(start_date) && !is.na(end_date)) {
          return(paste0(start_date, "/", end_date))
        }
      }

      # Try mm/yyyy format
      if (str_detect(parts[1], "^\\d{2}/\\d{4}$")) {
        start_date <- dmy(paste0("01/", parts[1]))
        end_month <- as.numeric(str_extract(parts[2], "^\\d{2}"))
        end_year <- as.numeric(str_extract(parts[2], "\\d{4}$"))
        end_date <- ymd(paste0(end_year, "-", end_month, "-01")) + months(1) - days(1)
        if (!is.na(start_date) && !is.na(end_date)) {
          return(paste0(start_date, "/", end_date))
        }
      }
    }

    if (str_detect(date_str, " - ")) {
      parts <- str_split(date_str, " - ")[[1]]
      start_date <- dmy(parts[1])
      end_date <- dmy(parts[2])
      if (!is.na(start_date) && !is.na(end_date)) {
        return(paste0(start_date, "/", end_date))
      }
    }

    # Return original if no pattern matches
    return(date_str)
  }

  report_metadata_clean <- report_metadata |>
    mutate(
      reporting_period = map_chr(reporting_period, parse_date_range),
      project_starting_and_end_date = map_chr(project_starting_and_end_date, parse_date_range)
    )

  # Fix 4: Standardize start_date format in metadata
  metadata_clean <- metadata_clean |>
    mutate(
      start_date = case_when(
        is.na(start_date) ~ as.Date(NA),
        # Handle "1 Mar 2023" format
        str_detect(start_date, "^\\d{1,2} \\w+ \\d{4}$") ~ dmy(start_date),
        # Handle "2023-09-01" format
        str_detect(start_date, "^\\d{4}-\\d{2}-\\d{2}$") ~ ymd(start_date),
        TRUE ~ as.Date(NA)  # For any unexpected formats
      )
    )

  # Fix 5: Replace -999999 placeholder values with NA in budget data
  budget_clean <- budget |>
    mutate(across(where(is.numeric), ~ ifelse(.x == -999999, NA, .x)))

  # Fix 6: Convert Yes/No to boolean in ethics data and ensure all logical type
  ethics_clean <- ethics |>
    mutate(across(starts_with("ethics_"), ~ {
      result <- case_when(
        toupper(as.character(.x)) == "YES" ~ TRUE,
        toupper(as.character(.x)) == "NO" ~ FALSE,
        toupper(as.character(.x)) == "TRUE" ~ TRUE,
        toupper(as.character(.x)) == "FALSE" ~ FALSE,
        is.na(.x) ~ NA,
        TRUE ~ NA  # For any unexpected values
      )
      # Explicitly convert to logical to ensure consistent type
      as.logical(result)
    }))

  cat("02_clean.R completed successfully\n")

  # Return updated data with cleaned metadata
  return(list(
    metadata_clean = metadata_clean,
    budget_long = budget_clean,
    ethics = ethics_clean,
    report_metadata_clean = report_metadata_clean,
    report_output = data$report_output,
    applicants = data$applicants,
    keywords = data$keywords,
    work_packages = data$work_packages,
    coapplicants = data$coapplicants
  ))
}
