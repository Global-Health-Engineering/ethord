# project_mapping: ETH Board Open Research Data (ORD) Program Project Metadata and Report Data

ETH Open Research Data dataset, A colletion of metadata and report data
of a CHF 15 million ETH domain program dedicated to increase the
visibility and the impact of their research within the scientific
community, the economy and society as a whole.

## Usage

``` r
project_mapping
```

## Format

A data frame with 76 rows and 5 variables:

- project_id:

  Unique identifier for each research project within the ETH Open
  Research Data dataset. (Examples: CONTRIBUTE/MAST,
  CONTRIBUTE/STILLBERGDAT, CONTRIBUTE/API-ROGER)

- document_path:

  File path to the document associated with the research project.
  (Examples: raw/ORD_files/Contribute/Ando/application/EPFL_Ando.pdf,
  raw/ORD_files/Contribute/Skaloud - 8th
  call/application/EPFL_Skaloud.pdf, raw/ORD_files/Contribute/Kim - 2nd
  call/application/ETHZ_Kim.pdf)

- project_category:

  Classification of the research project based on its purpose or funding
  type. (Examples: Contribute, Establish, Explore)

- project_acronym:

  Abbreviated identifier for the research project, typically
  representing its full title. (Examples: DCSM, FAIRGeo, FiRE)

- project_title:

  Title of the research project that describes its objectives and scope.
  (Examples: Mitigating spaceborne radio frequency interference through
  satellite database (SRFI-DB), Establishing the ecosystem for community
  driven scanning probe microscopy research and development, A
  standardized database framework for synthetic carbon-based solar
  fuels)
