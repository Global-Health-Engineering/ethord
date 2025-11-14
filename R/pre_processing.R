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

write.csv(metadata, "data_raw/application_metadata.csv", row.names = FALSE)
write.csv(budget, "data_raw/application_budget.csv", row.names = FALSE)
write.csv(ethics, "data_raw/application_ethics.csv", row.names = FALSE)

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
  "data_raw/report_metadata.csv",
  row.names = FALSE
)
write.csv(
  report_output,
  "data_raw/report_output.csv",
  row.names = FALSE
)

# TIDY FORMAT: Split numbered columns into separate tables
split_numbered_columns <- function(df, pattern, group_name) {
  cols <- grep(pattern, names(df), value = TRUE)
  if (length(cols) == 0) return(NULL)

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
    select(-column) |>
    pivot_wider(
      names_from = field,
      values_from = value
    ) |>
    mutate(index = as.numeric(index)) |>
    arrange(document_path, index)
}

# Split application metadata tables
applicants <- split_numbered_columns(metadata, "^data_all_applicants_\\d+", "data_all_applicants")
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

# Convert budget to long format (phases)
# Get phase 1 columns (ones without _2 suffix)
phase1_cols <- names(budget)[!grepl("_2$", names(budget))]
budget_phase1 <- budget |>
  select(all_of(phase1_cols)) |>
  mutate(phase = 1)

# Get phase 2 columns (ones with _2 suffix) and rename them
phase2_cols <- names(budget)[grepl("_2$", names(budget))]
budget_phase2 <- budget |>
  select(document_path, all_of(phase2_cols)) |>
  rename_with(~ str_remove(.x, "_2$"), all_of(phase2_cols)) |>
  filter(if_any(-c(document_path), ~ !is.na(.x))) |>
  mutate(phase = 2)

budget_long <- bind_rows(budget_phase1, budget_phase2)

# Remove split columns from original datasets (but keep budget as-is)
metadata_clean <- metadata |>
  select(-starts_with("data_all_applicants_"), -starts_with("data_keywords_"), -starts_with("data_work_packages_"))

report_metadata_clean <- report_metadata |>
  select(-starts_with("data_coapplicants_"))

# Split report coapplicants
coapplicants <- split_numbered_columns(report_metadata, "^data_coapplicants_\\d+", "data_coapplicants")

# Write cleaned original tables
write.csv(metadata_clean, "data_raw/application_metadata.csv", row.names = FALSE)
write.csv(budget_long, "data_raw/application_budget.csv", row.names = FALSE)
write.csv(report_metadata_clean, "data_raw/report_metadata.csv", row.names = FALSE)

# Write tidy tables with clear naming
write.csv(applicants, "data_raw/application_metadata_applicants.csv", row.names = FALSE)
write.csv(keywords, "data_raw/application_metadata_keywords.csv", row.names = FALSE)
write.csv(work_packages, "data_raw/application_metadata_work_packages.csv", row.names = FALSE)
write.csv(coapplicants, "data_raw/report_metadata_coapplicants.csv", row.names = FALSE)
