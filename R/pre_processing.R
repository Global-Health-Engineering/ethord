# LIBRARIES
packages <- c("dplyr", "tidyr", "stringr", "readr")
for (pkg in packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
    library(pkg, character.only = TRUE)
  }
}

# COMMON
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
      starts_with("data_phase1_")
    ) |>
    rename_with(
      ~ gsub("^data_phase2_", "data_", paste0(.x, "_2")),
      starts_with("data_phase2_")
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

write.csv(metadata, "inst/extdata/application_metadata.csv", row.names = FALSE)
write.csv(budget, "inst/extdata/application_budget.csv", row.names = FALSE)
write.csv(ethics, "inst/extdata/application_ethics.csv", row.names = FALSE)

# REPORT: METADATA, OUTPUT
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
      # Extract category: everything before last _quantity, _descriptions_N, or _urls_N
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

report_metadata <- read_csv(
  "inst/extdata/raw/report_metadata_establish_contribute_explore.csv",
  show_col_types = FALSE
) |>
  filter_columns() |>
  tidy()
report_output <- read_csv(
  "inst/extdata/raw/report_output_establish_contribute_explore.csv",
  show_col_types = FALSE
) |>
  filter_columns() |>
  process_report_output()

write.csv(
  report_metadata,
  "inst/extdata/report_metadata.csv",
  row.names = FALSE
)
write.csv(
  report_output,
  "inst/extdata/report_output.csv",
  row.names = FALSE
)
