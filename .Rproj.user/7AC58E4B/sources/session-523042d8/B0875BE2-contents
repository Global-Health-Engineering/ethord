import sys
import logging
from pathlib import Path

from llama_cloud import ExtractConfig, ExtractMode

from ghe_extract.core import LlamaCloudExtractor
from ORDApplication import ORDMetadata, ORDBudget, ORDBudgetEstablish, ORDEthics
from ORDReport import ORDReportMetadata, ORDReportOutput

logger = logging.getLogger(__name__)


def main():
    """Main entry point for ORD document extraction."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <directory>")
        sys.exit(1)

    directory = str(Path(sys.argv[1]))

    extractor = LlamaCloudExtractor()

    extraction_mode=ExtractMode.PREMIUM
    parse_model="gemini-2.5-pro"

    # Base extraction strategy - common to all extractions
    base_system_prompt = """
  EXTRACTION STRATEGY:
  1. PRIMARY: Look for data in the specified location/table/section
  2. FALLBACK: If not found, search broader document context for semantically equivalent information
  3. FLEXIBILITY: Allow for format variations, OCR errors, and synonym usage

  LOCATION FLEXIBILITY:
  - Handle table format variations (column/row order, spacing, naming)
  - Consider synonyms and equivalent terms
  - Account for OCR/parsing errors that may affect document quality

  QUALITY STANDARDS:
  - Extract actual values found in the document
  - If uncertain, provide best interpretation with appropriate confidence
  - Only return null if the information category truly doesn't exist
  - Convert abbreviated amounts (k=1000) to full numbers where applicable
  """

    # Schema-specific prompts
    metadata_prompt = f"""{base_system_prompt}

  METADATA EXTRACTION FOCUS:
  - Project identification: title, acronym, duration, start date
  - Applicant details: names, institutions, functions, addresses
  - Project categorization: Explore/Establish/Contribute classification
  - Keywords and abstract information from research proposal sections
  """

    budget_prompt = f"""{base_system_prompt}

  BUDGET EXTRACTION FOCUS:
  - Look for "Total requested amount in CHF" for main budget figure
  - Personnel categories: Senior Staff, Postdocs, Students, Other
  - Cost categories: Travel, Equipment, Publications, Conferences, Subcontracting
  - Extract numerical CHF values from budget tables
  - Two-phase projects: separate Phase 1 and Phase 2 budget sections
  """

    ethics_prompt = f"""{base_system_prompt}

  ETHICS EXTRACTION FOCUS:
  - Systematic Yes/No questions organized by numbered categories
  - Categories: Human subjects, Personal data, Animals, International activities, Environment, AI
  - Extract exact Yes/No responses, not explanatory text
  - Look for "ETHICAL ISSUES FORM" section with structured questions
  """

    report_metadata_prompt = f"""{base_system_prompt}

  REPORT METADATA FOCUS:
  - Project identification in "General information" table
  - Report type classification: Final vs Intermediate
  - Main applicant details and institutional affiliations
  - Co-applicant information in structured table format
  - Reporting periods and project dates
  """

    report_output_prompt = f"""{base_system_prompt}

  REPORT OUTPUT FOCUS:
  - 15 standard output categories in "List of Outputs" table
  - Each category: quantity number, descriptions list, URLs list
  - Separate descriptions from URLs even when mixed in same cell
  - Academic collaborations vs Industrial partnerships (distinct categories)
  - Preserve all detailed descriptions and web addresses
  """
    use_reasoning=True
    confidence_scores=True
    cite_sources=True
    high_resolution_mode=True

    skip_existing=True
    output_base="inst/extdata/raw"

    def extract_wrapper(schema, output_prefix, include_patterns=None, exclude_patterns=None,
                                mode=extraction_mode):
        """Wrapper for common extraction parameters"""

        # Map schema to appropriate system prompt
        schema_prompt_map = {
            'ORDMetadata': metadata_prompt,
            'ORDBudget': budget_prompt,
            'ORDBudgetEstablish': budget_prompt,
            'ORDEthics': ethics_prompt,
            'ORDReportMetadata': report_metadata_prompt,
            'ORDReportOutput': report_output_prompt
        }

        schema_name = schema.__name__
        system_prompt = schema_prompt_map.get(schema_name, base_system_prompt)

        return extractor.extract_directory(
            directory=directory,
            schema=schema,
            config=ExtractConfig(
                extraction_mode=mode,
                parse_model=parse_model,
                system_prompt=system_prompt,
                use_reasoning=use_reasoning,
                confidence_scores=confidence_scores,
                cite_sources=cite_sources,
                high_resolution_mode=high_resolution_mode
            ),
            output_prefix=output_prefix,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            skip_existing=skip_existing,
            output_base=output_base
        )

    # Extract metadata for establish projects
    extract_wrapper(ORDMetadata, "application_metadata_establish",
                           include_patterns=["application", "establish"])

    # Extract two-phase budget for establish projects
    extract_wrapper(ORDBudgetEstablish, "application_budget_establish",
                           include_patterns=["application", "establish"])

    # Extract ethics for establish projects
    extract_wrapper(ORDEthics, "application_ethics_establish",
                           include_patterns=["application", "establish"])

    # Extract metadata for single-phase projects
    extract_wrapper(ORDMetadata, "application_metadata_contribute_explore",
                           include_patterns="application", exclude_patterns="establish")

    # Extract single-phase budget for application-only projects
    extract_wrapper(ORDBudget, "application_budget_contribute_explore",
                           include_patterns="application", exclude_patterns="establish")

    # Extract ethics for application-only projects
    extract_wrapper(ORDEthics, "application_ethics_contribute_explore",
                           include_patterns="application", exclude_patterns="establish")

    # Extract report metadata
    extract_wrapper(ORDReportMetadata, "report_metadata_establish_contribute_explore",
                           include_patterns="report")

    # Extract report outputs
    extract_wrapper(ORDReportOutput, "report_output_establish_contribute_explore",
                           include_patterns="report")


if __name__ == "__main__":
    main()