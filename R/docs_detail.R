#' docs_detail: ETH Board Open Research Data (ORD) Program Project Metadata and Report Data
#' 
#' This data package contains metadata and report data from 96 research projects funded by the joint Open Research Data (ORD) program of ETH Zurich, EPFL, and the four research institutes of the ETH Domain. The package includes project-level metadata, such as project titles, descriptions, and categorizations (Establish, Explore, Contribute), as well as data extracted from reports submitted by each project, providing insights into the projects' objectives, methods, outcomes, and impacts.
#' 
#' @format A tibble with 7 rows and 19 variables
#' \describe{
#'   \item{project_id}{A unique identifier for each project, represented as a numerical value.}
#'   \item{call_category}{The category of the project call, with possible values including Explore and Contribute.}
#'   \item{applicant_id}{A unique identifier for the applicant, typically in the format ORD followed by a series of numbers.}
#'   \item{main_applicant_institution_name}{The name of the main institution associated with the applicant.}
#'   \item{applicant_type}{The type of applicant, categorized as either Primary or Secondary.}
#'   \item{applicant_title}{The title of the applicant, such as Prof. Dr.}
#'   \item{applicant_first_name}{The first name of the applicant.}
#'   \item{applicant_last_name}{The last name of the applicant.}
#'   \item{applicant_institution}{The institution affiliated with the applicant.}
#'   \item{applicant_department_name}{The name of the department within the applicant's institution.}
#'   \item{applicant_lab_name}{The name of the laboratory associated with the applicant.}
#'   \item{applicant_orcid_id}{The ORCID identifier for the applicant.}
#'   \item{title}{The title of the project.}
#'   \item{acronym}{A shortened acronym representing the project title.}
#'   \item{abstract}{A brief summary or abstract of the project.}
#'   \item{keywords}{Relevant keywords associated with the project.}
#'   \item{project_start_dd_mm_yyyy}{The start date of the project in the format DD.MM.YYYY.}
#'   \item{project_duration_months}{The duration of the project in months, represented as a numerical value.}
#'   \item{funding_requested}{The amount of funding requested for the project, represented as a numerical value.}
#' }
"docs_detail"
