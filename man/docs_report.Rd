% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/docs_report.R
\docType{data}
\name{docs_report}
\alias{docs_report}
\title{docs_report: ETH Board Open Research Data (ORD) Program Project Metadata and Report Data}
\format{
A tibble with 60 rows and 7 variables
\describe{
\item{project_id}{A unique identifier for each project, represented as a numerical value.}
\item{item_id}{A unique identifier for each item within a project, represented as a numerical value with decimal places.}
\item{item_name_long}{A detailed name describing the item, such as 'New or enhanced webs' or 'New or enhanced data'.}
\item{item_name_short}{A brief name summarizing the item, such as 'website', 'repository', or 'dataset'.}
\item{quantity}{The number of items, represented as a discrete numerical value.}
\item{description}{A text description providing additional context about the item.}
\item{link}{A URL linking to the item or its associated resource, such as a website or repository.}
}
}
\usage{
docs_report
}
\description{
This data package contains metadata and report data from 96 research projects funded by the joint Open Research Data (ORD) program of ETH Zurich, EPFL, and the four research institutes of the ETH Domain. The package includes project-level metadata, such as project titles, descriptions, and categorizations (Establish, Explore, Contribute), as well as data extracted from reports submitted by each project, providing insights into the projects' objectives, methods, outcomes, and impacts.
}
\keyword{datasets}
