# 01_TRANSFORM: Basic processing, name cleaning, and column splitting
# Uses existing working code from pre_processing.R

transform_data <- function() {
  # LIBRARIES
  packages <- c("dplyr", "tidyr", "stringr", "readr")
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE)) {
      install.packages(pkg)
      library(pkg, character.only = TRUE)
    }
  }

  # COMMON FUNCTIONS
  filter_columns <- function(df) {
    df |>
      select(document_path, starts_with("data_"))
  }

  tidy <- function(df) {
    df |>
      mutate(across(where(is.character), ~ na_if(., "")))
  }

  # APPLICATION: BUDGET, ETHICS, METADATA
  rename_budget_phases <- function(df) {
    df |>
      rename_with(
        ~ gsub("^data_phase1_", "data_", .x),
        .cols = starts_with("data_phase1_")
      ) |>
      rename_with(
        ~ gsub("^data_phase2_", "data_", paste0(.x, "_2")),
        .cols = starts_with("data_phase2_")
      )
  }

  process_csv_pair <- function(
    establish_file,
    only_file,
    is_budget = FALSE,
    is_metadata = FALSE
  ) {
    establish_df <- read_csv(establish_file, show_col_types = FALSE) |>
      filter_columns()
    only_df <- read_csv(only_file, show_col_types = FALSE) |> filter_columns()

    if (is_budget) {
      establish_df <- rename_budget_phases(establish_df)
    }

    bind_rows(establish_df, only_df) |>
      tidy()
  }

  # SPLIT NUMBERED COLUMNS FUNCTION
  split_numbered_columns <- function(df, pattern, group_name) {
    cols <- grep(pattern, names(df), value = TRUE)
    if (length(cols) == 0) {
      return(data.frame())
    }

    df |>
      select(document_path, all_of(cols)) |>
      mutate(across(everything(), as.character)) |>
      pivot_longer(
        cols = -document_path,
        names_to = "column",
        values_to = "value",
        values_drop_na = TRUE
      ) |>
      filter(!is.na(value), value != "", value != "[]") |>
      mutate(
        index = str_extract(column, "\\d+"),
        field = str_remove(column, paste0("^", group_name, "_\\d+_?"))
      ) |>
      filter(field != "") |> # Remove empty field names
      select(-column) |>
      pivot_wider(
        names_from = field,
        values_from = value
      ) |>
      mutate(index = as.numeric(index)) |>
      arrange(document_path, index)
  }

  # PROCESS MAIN DATASETS
  metadata <- process_csv_pair(
    "inst/extdata/raw/application_metadata_establish.csv",
    "inst/extdata/raw/application_metadata_contribute_explore.csv",
    is_metadata = TRUE
  )

  budget <- process_csv_pair(
    "inst/extdata/raw/application_budget_establish.csv",
    "inst/extdata/raw/application_budget_contribute_explore.csv",
    is_budget = TRUE
  )

  ethics <- process_csv_pair(
    "inst/extdata/raw/application_ethics_establish.csv",
    "inst/extdata/raw/application_ethics_contribute_explore.csv"
  )

  # REPORT DATA
  report_metadata <- read_csv(
    "inst/extdata/raw/report_metadata_establish_contribute_explore.csv",
    show_col_types = FALSE
  ) |>
    filter_columns() |>
    tidy()

  # PROCESS REPORT OUTPUT FUNCTION
  process_report_output <- function(df) {
    df |>
      tidy() |>
      mutate(across(everything(), as.character)) |>
      pivot_longer(
        cols = -document_path,
        names_to = "column",
        values_to = "value",
        values_drop_na = TRUE
      ) |>
      filter(value != "[]") |>
      mutate(
        # Extract category name
        category = str_replace(column, "^data_", "") |>
          str_replace("_quantity$", "") |>
          str_replace("_(descriptions|urls)_\\d+$", ""),
        # Extract metric type
        metric = case_when(
          str_detect(column, "_quantity$") ~ "quantity",
          str_detect(column, "_descriptions_") ~ "descriptions",
          str_detect(column, "_urls_") ~ "urls"
        ),
        # Extract index number for descriptions/urls
        index = str_extract(column, "(?<=_(descriptions|urls)_)\\d+$")
      ) |>
      select(-column) |>
      pivot_wider(
        names_from = metric,
        values_from = value
      ) |>
      group_by(document_path, category) |>
      fill(quantity, .direction = "downup") |>
      ungroup() |>
      mutate(
        quantity = as.numeric(quantity),
        index = as.numeric(index)
      ) |>
      filter(!is.na(index)) |>
      arrange(document_path, category, index)
  }

  report_output <- read_csv(
    "inst/extdata/raw/report_output_establish_contribute_explore.csv",
    show_col_types = FALSE
  ) |>
    filter_columns() |>
    process_report_output()

  # SPLIT NUMBERED COLUMNS
  applicants <- split_numbered_columns(metadata, "^data_all_applicants_\\d+", "data_all_applicants")

  # Keywords have no subcategories, handle separately
  keywords <- metadata |>
    select(document_path, starts_with("data_keywords_")) |>
    pivot_longer(
      cols = -document_path,
      names_to = "index",
      values_to = "keyword",
      values_drop_na = TRUE
    ) |>
    filter(!is.na(keyword), keyword != "", keyword != "[]") |>
    mutate(index = as.numeric(str_extract(index, "\\d+"))) |>
    arrange(document_path, index)

  work_packages <- split_numbered_columns(metadata, "^data_work_packages_\\d+", "data_work_packages")
  coapplicants <- split_numbered_columns(report_metadata, "^data_coapplicants_\\d+", "data_coapplicants")

  # CONVERT BUDGET TO LONG FORMAT
  phase1_cols <- names(budget)[!grepl("_2$", names(budget))]
  budget_phase1 <- budget |>
    select(all_of(phase1_cols)) |>
    mutate(phase = 1)

  phase2_cols <- names(budget)[grepl("_2$", names(budget))]
  budget_phase2 <- budget |>
    select(document_path, all_of(phase2_cols)) |>
    rename_with(~ str_remove(.x, "_2$"), all_of(phase2_cols)) |>
    filter(if_any(-c(document_path), ~ !is.na(.x))) |>
    mutate(phase = 2)

  budget_long <- bind_rows(budget_phase1, budget_phase2)

  # CLEAN MAIN DATASETS (remove split columns)
  metadata_clean <- metadata |>
    select(-starts_with("data_all_applicants_"), -starts_with("data_keywords_"), -starts_with("data_work_packages_"))

  report_metadata_clean <- report_metadata |>
    select(-starts_with("data_coapplicants_"))

  # Remove data_ prefix from all column names except document_path
  remove_data_prefix <- function(df) {
    df |>
      rename_with(~ str_remove(.x, "^data_"), .cols = starts_with("data_"))
  }

  # Apply prefix removal to all datasets
  metadata_clean <- remove_data_prefix(metadata_clean)
  budget_long <- remove_data_prefix(budget_long)
  ethics <- remove_data_prefix(ethics)
  report_metadata_clean <- remove_data_prefix(report_metadata_clean)
  applicants <- remove_data_prefix(applicants)
  keywords <- remove_data_prefix(keywords)
  work_packages <- remove_data_prefix(work_packages)
  coapplicants <- remove_data_prefix(coapplicants)

  # Print completion message
  cat("01_transform.R completed successfully\n")

  # Return all datasets as a list
  return(list(
    metadata_clean = metadata_clean,
    budget_long = budget_long,
    ethics = ethics,
    report_metadata_clean = report_metadata_clean,
    report_output = report_output,
    applicants = applicants,
    keywords = keywords,
    work_packages = work_packages,
    coapplicants = coapplicants
  ))
}
