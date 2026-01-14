# Changelog

## ethord 0.1.0 (2026-01-14)

### Major Changes - Complete Dataset Restructuring

This release represents a **breaking change** with a complete
restructuring of the package datasets to provide more granular and
structured access to ETH Board Open Research Data (ORD) program
information.

#### Removed Datasets

The following datasets from version 0.0.3 have been removed and replaced
with a new structure:

- `portal` - Project metadata from ORD portal
- `docs_detail` - Detailed project information
- `docs_proposal` - Project proposal documents
- `docs_report` - Project report data

#### New Dataset Structure

The package now provides **10 structured datasets** organized by data
type:

##### Application Data

- **`application_budget`** - Budget information from project
  applications (78 projects, 16 variables)
  - Personnel costs (senior staff, postdocs, PhDs, students,
    technicians)
  - Material, travel, publication, and other costs
  - Total budget per project
- **`application_ethics`** - Ethics-related information from
  applications (77 projects)
  - Human subjects research declarations
  - Animal research declarations
  - Recombinant DNA usage
  - Hazardous materials handling
- **`application_metadata`** - Core project metadata (105 projects,
  comprehensive variables)
  - Project titles, acronyms, abstracts
  - Keywords and descriptions
  - Start dates and duration
  - Funding amounts requested
- **`application_metadata_applicants`** - Detailed applicant information
  (114 records)
  - Applicant names, titles, ORCID IDs
  - Institutions, departments, laboratories
  - Primary vs. secondary applicants
- **`application_metadata_keywords`** - Project keywords (304 keyword
  entries)
  - Structured keyword associations
  - Searchable by project
- **`application_metadata_work_packages`** - Work package descriptions
  (274 entries)
  - Detailed work package information per project

##### Reporting Data

- **`report_metadata`** - Metadata from project reports (64 reports)
  - Reporting periods
  - Project progress information
- **`report_metadata_coapplicants`** - Co-applicant information from
  reports (133 entries)
  - Co-applicant details and roles
- **`report_output`** - Project outputs and deliverables (1034 output
  records)
  - Publications, datasets, software
  - Presentations and other research outputs
  - Organized by output category and metrics

##### Cross-Reference Data

- **`project_mapping`** - Maps projects across datasets (77 projects)
  - Project IDs and categories (Contribute, Explore, Establish)
  - Cross-reference between application and report data

### Data Improvements

#### Data Quality Enhancements

- **Standardized date formats** - All dates converted to YYYY-MM-DD
  format
- **Removed empty placeholder columns** - Cleaner, more focused datasets
- **Consistent project identifiers** - `project_id` used across all
  datasets for joining
- **Cleaned edge cases** - Better handling of missing values and data
  inconsistencies
- **Tidy data structure** - Normalized tables following tidy data
  principles

#### Data Processing Pipeline

- Added comprehensive data transformation pipeline
  (`data_raw/01_transform.R`)
- Implemented data cleaning procedures (`data_raw/02_clean.R`)
- Created data processing and ID management (`data_raw/03_process.R`)
- Automated pipeline execution (`data_raw/run_all.R`)

### Package Infrastructure

#### Technical Improvements

- Updated minimum R version requirement to **R \>= 4.1.0** (required for
  native pipe `|>`)
- Added package dependencies: dplyr, tidyr, stringr, lubridate, purrr,
  readr, fs
- Excluded raw data files from package build for portability
- Added comprehensive package documentation
- Created `CLAUDE.md` for AI-assisted development

#### Documentation

- Complete rewrite of README with new dataset structure
- Updated all dataset documentation with roxygen2
- Added data dictionary with 98+ variable definitions
- Improved variable descriptions and metadata

### Migration Guide

Users of version 0.0.3 will need to update their code:

#### Old Code (v0.0.3)

``` r
library(ethord)

# Access portal data
portal |>
  filter(category == "Contribute")
```

#### New Code (v0.1.0)

``` r
library(ethord)

# Access application metadata
application_metadata |>
  left_join(project_mapping, by = "project_id") |>
  filter(project_category == "Contribute")

# Access budget information
application_budget |>
  left_join(project_mapping, by = "project_id")

# Access research outputs
report_output |>
  left_join(project_mapping, by = "project_id")
```

#### Key Changes for Users

1.  **Join datasets using `project_id`** - Datasets are now normalized;
    use joins to combine information
2.  **Use `project_mapping` for categories** - Project categories
    (Contribute/Explore/Establish) are in `project_mapping`
3.  **More granular access** - Access specific data types directly
    instead of one large table
4.  **Better column names** - All variables follow consistent naming
    conventions

### Data Source

All data extracted from official ETH Board Open Research Data (ORD)
program documentation including: - Project application forms -
Scientific reports - Intermediate reports - Project metadata from the
ORD portal

### Notes

- Raw JSON extraction files are available in the GitHub repository but
  excluded from the package build
- Data processing scripts are located in `data_raw/` for reproducibility
- All datasets available as both `.rda` (R format) and `.csv` (portable
  format) in `inst/extdata/`

------------------------------------------------------------------------

## ethord 0.0.3 (2025-07-28)

### Changes

- Updated DOI
- Fixed date formatting to YYYY-MM-DD
- Fixed broken download links
- Removed applicant gender variables for privacy
- Added example visualization plot
- Updated package website configuration

------------------------------------------------------------------------

## ethord 0.0.2

Initial release with portal, docs_detail, docs_proposal, and docs_report
datasets.
