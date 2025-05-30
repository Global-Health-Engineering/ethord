#' portal: ETH Board Open Research Data (ORD) Program Project Metadata and Report Data
#' 
#' This data package contains metadata and report data from 96 research projects funded by the joint Open Research Data (ORD) program of ETH Zurich, EPFL, and the four research institutes of the ETH Domain. The package includes project-level metadata, such as project titles, descriptions, and categorizations (Establish, Explore, Contribute), as well as data extracted from reports submitted by each project, providing insights into the projects' objectives, methods, outcomes, and impacts.
#' 
#' @format A tibble with 96 rows and 8 variables
#' \describe{
#'   \item{url}{The URL linking to the specific research project's details or webpage.}
#'   \item{title}{The title of the research project.}
#'   \item{category}{The category or classification of the research project, such as Contribute, Explore, or Establish.}
#'   \item{institutions}{The institutions involved in the research project, such as EPFL, ETH Zurich, or Empa.}
#'   \item{data_type}{The type of data associated with the research project, such as Microstructure data, Environmental data, or Medical data.}
#'   \item{field}{The field of study or discipline of the research project, such as Materials Science, Earth sciences, or Life sciences.}
#'   \item{researchers}{The names of the researchers involved in the project.}
#'   \item{abstract}{A brief summary or abstract of the research project.}
#' }
"portal"
