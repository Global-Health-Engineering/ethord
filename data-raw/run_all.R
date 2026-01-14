# RUN ALL: Execute the complete pipeline

# Load pipeline functions
source("R/01_transform.R")
source("R/02_clean.R")
source("R/03_process.R")

# Execute pipeline
run_pipeline <- function() {
  cat("Starting ethord data pipeline...\n\n")

  # Step 1: Transform
  cat("Step 1: Transform raw data\n")
  data_01 <- transform_data()

  # Step 2: Clean
  cat("\nStep 2: Clean data\n")
  data_02 <- clean_data(data_01)

  # Step 3: Process and save
  cat("\nStep 3: Process IDs and save final datasets\n")
  final_data <- process_data(data_02)

  cat("\nPipeline completed successfully!\n")
  cat("Final datasets saved to data_raw/\n")

  return(final_data)
}

# Run the pipeline
if (interactive() || !exists("SOURCED")) {
  result <- run_pipeline()
}
