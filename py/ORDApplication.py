"""
ORD Application Schemas divided into three focused extraction schemas for better performance:

1. ORDMetadata: Project information and applicant details
2. ORDBudget/ORDBudgetEstablish: Budget information (single/two-phase)
3. ORDEthics: Ethics-related questions

This division reduces token consumption and improves extraction accuracy by focusing
on specific data domains in separate extraction passes.
"""

from typing import List, Literal
from pydantic import BaseModel, Field
from ghe_extract.extraction_guide import extraction_guide

# Configuration
USE_EVIDENCE = False

# Conditional type imports/assignments
if USE_EVIDENCE:
    from ghe_extract.WithEvidence import StringWithEvidence, IntWithEvidence, FloatWithEvidence, LiteralWithEvidence
else:
    # Standard type aliases when not using evidence
    StringWithEvidence = str
    IntWithEvidence = int
    FloatWithEvidence = float

    def LiteralWithEvidence(*options):
        """Factory function to create Literal types when not using evidence"""
        return Literal[options] if len(options) > 1 else Literal[options[0]]

def budget_field(section: str, variable_row: str) -> Field:
    """Create a budget field matching the standard ORD budget table format"""
    return Field(default=None, **extraction_guide(
        description=f"Extract CHF amount from budget table for '{variable_row}'. Look for numerical values in the 'Total in CHF' column.",
        section="Budget table",
    ))


class ORDApplicant(BaseModel):
    """Individual applicant information - part of extended extraction"""
    eth_domain_institution: LiteralWithEvidence("ETH Zürich", "EPFL", "PSI", "WSL", "Empa", "Eawag", "other") = Field(**extraction_guide(
        variable="Which ETH Domain do you belong to?",
        options=["ETH Zürich", "EPFL", "PSI", "WSL", "Empa", "Eawag", "other"],
        include="details of one person"
    ))
    function_title: StringWithEvidence = Field(**extraction_guide(
        variable="Function (Title)",
        include="details of one person"
    ))
    first_name: StringWithEvidence = Field(**extraction_guide(
        variable="First name(s)",
        include="details of one person"
    ))
    surname: StringWithEvidence = Field(**extraction_guide(
        variable="Surname(s)",
        include="details of one person"
    ))
    postcode: IntWithEvidence = Field(**extraction_guide(
        description="4 digit postcode",
        variable="Name and Address of the Laboratory",
        include="details of one person"
    ))

    class Config:
        use_enum_values = True


class ORDWorkPackage(BaseModel):
    """Work package information - part of extended extraction"""
    wp_identifier: LiteralWithEvidence("WP1", "WP2", "WP3", "WP4", "WP5", "WP6", "WP7", "WP8", "WP9", "other") = Field(**extraction_guide(
        description="Work package identifier",
        options = ["WP1", "WP2", "WP3", "WP4", "WP5", "WP6", "WP7", "WP8", "WP9", "other"]
    ))
    wp_title: StringWithEvidence = Field(**extraction_guide(
        description="Work package title/short description"
    ))

    class Config:
        use_enum_values = True


class ORDBudget(BaseModel):
    """
    ORD Budget Schema: Single-phase budget extraction.

    Extracts detailed budget breakdown for single-phase projects.
    """

    # Personnel costs
    total_budget_personnel_senior_staff: FloatWithEvidence = budget_field("Budget table", "Senior Staff")
    total_budget_personnel_postdocs: FloatWithEvidence = budget_field("Budget table", "Postdocs")
    total_budget_personnel_students: FloatWithEvidence = budget_field("Budget table", "Students")
    total_budget_personnel_other: FloatWithEvidence = budget_field("Budget table", "Other")
    total_budget_personnel_total_direct: FloatWithEvidence = budget_field("Budget table", "Total Direct Costs for Personnel")

    # Other costs
    total_budget_travel: FloatWithEvidence = budget_field("Budget table", "Travel")
    total_budget_equipment: FloatWithEvidence = budget_field("Budget table", "Equipment")
    total_budget_other_publication_fees: FloatWithEvidence = budget_field("Budget table", "Other Publications")
    total_budget_other_conferences_workshops: FloatWithEvidence = budget_field("Budget table", "Other Conferences and workshops")
    total_budget_other_other: FloatWithEvidence = budget_field("Budget table", "Other Other")
    total_budget_other_total_direct: FloatWithEvidence = budget_field("Budget table", "Total Other Direct Costs")

    # Totals
    total_budget_total_direct: FloatWithEvidence = budget_field("Budget table", "Total Direct Costs")
    total_budget_subcontracting: FloatWithEvidence = budget_field("Budget table", "Subcontracting")
    total_budget_total_costs: FloatWithEvidence = budget_field("Budget table", "Total Costs")

    class Config:
        use_enum_values = True


class ORDMetadata(BaseModel):
    """
    ORD Application Metadata Schema: Project information and applicant details.

    Focuses on extracting:
    - Project categorization and basic details
    - Main applicant information
    - All project participants
    - Work packages
    - Total budget requested (single summary field)
    """

    # Call and project basic info
    project_category: LiteralWithEvidence("Explore Projects", "Establish Projects", "Contribute Projects") = Field(default=None, **extraction_guide(
        description="Which category of projects does this project belong to",
        section="Document title. ETH-Domain ORD Program - Measure ...",
        options=["Explore Projects", "Establish Projects", "Contribute Projects"]
    ))

    # Main applicant details
    main_applicant_institution: LiteralWithEvidence("ETH Zürich", "EPFL", "PSI", "WSL", "Empa", "Eawag", "other") = Field(**extraction_guide(
        description="Main applicant's institution",
        variable="Which ETH Domain do you belong to?",
        section="APPLICANT DETAILS",
        options=["ETH Zürich", "EPFL", "PSI", "WSL", "Empa", "Eawag", "other"],
        include="details of one person"
    ))
    main_applicant_function: StringWithEvidence = Field(default=None, **extraction_guide(
        description="Main applicant's function",
        variable="Function (Title)",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    main_applicant_first_name: StringWithEvidence = Field(**extraction_guide(
        description="Main applicant's first name",
        variable="First name(s)",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    main_applicant_surname: StringWithEvidence = Field(**extraction_guide(
        description="Main applicant's surnname",
        variable="Surname(s)",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    main_applicant_laboratory_name: StringWithEvidence = Field(default=None, **extraction_guide(
        description="Main applicant's laboratory",
        variable="Laboratory name",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    main_applicant_postcode: IntWithEvidence = Field(default=None, **extraction_guide(
        description="Main applicant's postcode",
        variable="Postcode / Zipcode",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    main_applicant_city: StringWithEvidence = Field(default=None, **extraction_guide(
        description="Main applicant's city",
        variable="City",
        section="APPLICANT DETAILS",
        include="details of one person, the main applicant"
    ))
    all_applicants: List[ORDApplicant] = Field(default=[], **extraction_guide(
        section="APPLICANT DETAILS",
        format_spec="Comma-separated list",
        include=["All project applicants and co-applicants, but only once, do not include same person several times"]
    ))

    # Project details
    project_title: StringWithEvidence = Field(**extraction_guide(
        variable="Project title",
        section="RESEARCH PROPOSAL"
    ))
    project_acronym: StringWithEvidence = Field(default=None, **extraction_guide(
        variable="Acronym of the project",
        section="RESEARCH PROPOSAL"
    ))
    project_abstract: StringWithEvidence = Field(default=None, **extraction_guide(
        variable="Abstract",
        section="RESEARCH PROPOSAL"
    ))
    keywords: List[StringWithEvidence] = Field(default=None, **extraction_guide(
        variable="Project keywords (up to 5)",
        section="RESEARCH PROPOSAL",
        format_spec="comma-separated list"
    ))
    start_date: StringWithEvidence = Field(default=None, **extraction_guide(
        variable="Proposed Starting Date",
        section="RESEARCH PROPOSAL"
    ))
    project_duration_months: IntWithEvidence = Field(default=None, **extraction_guide(
        variable="Project duration",
        section="RESEARCH PROPOSAL",
        format_spec="months"
    ))
    total_budget_requested: FloatWithEvidence = Field(**extraction_guide(
        section="BUDGET",
        variable="Total requested amount",
        format_spec="CHF"
    ))

    # Work packages
    work_packages: List[ORDWorkPackage] = Field(default=[], **extraction_guide(
        description="Work packages, tasks, and milestones"
    ))

    class Config:
        use_enum_values = True


class ORDEthics(BaseModel):
    """
    ORD Ethics Schema: Ethics-related questions extraction.

    Extracts all ethics-related Yes/No questions from the ethics form.
    """

    # Ethics fields
    ethics_human_embryonic_stem_cells: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve Human Embryonic Stem Cells (hESCs)?",
        options=["Yes", "No"]
    ))
    ethics_human_embryos: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve the use of human embryos?",
        options=["Yes", "No"]
    ))
    ethics_human_participants: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve human participants?",
        options=["Yes", "No"]
    ))
    ethics_human_interventions: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve interventions (physical also including imaging technology, behavioural treatments, etc.) on the study participants?",
        options=["Yes", "No"]
    ))
    ethics_clinical_study: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve conducting a clinical study as defined by the Federal Act on Research involving Human Beings and the Ordinance on Clinical Trials in Human Research (using pharmaceuticals, biologicals, radiopharmaceuticals, or advanced therapy medicinal products)?",
        options=["Yes", "No"]
    ))
    ethics_human_cells_tissues: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve the use of human cells or tissues?",
        options=["Yes", "No"]
    ))
    ethics_personal_data: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve processing of personal data?",
        options=["Yes", "No"]
    ))
    ethics_personal_data_further_processing: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve further processing of previously collected personal data (including use of preexisting data sets or sources, merging existing data sets)?",
        options=["Yes", "No"]
    ))
    ethics_personal_data_export_switzerland: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Is it planned to export personal data from Switzerland to countries outside Switzerland?",
        options=["Yes", "No"]
    ))
    ethics_personal_data_import_switzerland: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Is it planned to import personal data from countries outside Switzerland into Switzerland?",
        options=["Yes", "No"]
    ))
    ethics_personal_data_criminal: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve processing of personal data related to criminal convictions or offences?",
        options=["Yes", "No"]
    ))
    ethics_animals: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve animals?",
        options=["Yes", "No"]
    ))
    ethics_activities_outside_switzerland: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Will some of the activities be carried out outside Switzerland?",
        options=["Yes", "No"]
    ))
    ethics_outside_countries_ethics_issues: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="In case countries outside Switzerland are involved, do the activities undertaken in these countries raise potential ethics issues?",
        options=["Yes", "No"]
    ))
    ethics_local_resources: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Is it planned to use local resources (tissue samples, genetic material, live animals, human remains, etc.)?",
        options=["Yes", "No"]
    ))
    ethics_import_material: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Is it planned to use local resources (e.g. animal and/or human tissue samples, genetic material, live animals, human remains, materials of historical value, endangered fauna or flora samples, etc.)?",
        options=["Yes", "No"]
    ))
    ethics_export_material: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Is it planned to export any material (other than data) from Switzerland to countries outside Switzerland?",
        options=["Yes", "No"]
    ))
    ethics_low_middle_income_countries: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve low and/or lower middle income countries?",
        options=["Yes", "No"]
    ))
    ethics_individuals_at_risk: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Could the situation in the country put the individuals taking part in the activity at risk?",
        options=["Yes", "No"]
    ))
    ethics_environmental_harm: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve the use of substances or processes that may cause harm to the environment, to animals or plants (during the implementation of the activity or further to the use of the results, as a possible impact)?",
        options=["Yes", "No"]
    ))
    ethics_endangered_species: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity deal with endangered fauna and/or flora / protected areas?",
        options=["Yes", "No"]
    ))
    ethics_human_harm: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve the use of substances or processes that may cause harm to humans, including those performing the activity (during the implementation of the activity or further to the use of the results, as a possible impact)?",
        options=["Yes", "No"]
    ))
    ethics_artificial_intelligence: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Does this activity involve the development, deployment and/or use of Artificial Intelligence?",
        options=["Yes", "No"]
    ))
    ethics_other_issues: LiteralWithEvidence("Yes", "No") = Field(default=None, **extraction_guide(
        section="5 - ETHICAL ISSUES FORM",
        variable="Are there any other ethics issues that should be taken into consideration?",
        options=["Yes", "No"]
    ))

    class Config:
        use_enum_values = True


class ORDBudgetEstablish(BaseModel):
    """
    ORD Budget Schema: Two-phase budget extraction.

    Extracts detailed budget breakdown for two-phase "Establish" projects.
    """

    # Phase 1 budget fields
    phase1_total_budget_personnel_senior_staff: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Personnel Senior Staff")
    phase1_total_budget_personnel_postdocs: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Personnel Postdocs")
    phase1_total_budget_personnel_students: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Personnel Students")
    phase1_total_budget_personnel_other: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Personnel Other")
    phase1_total_budget_personnel_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Total Direct Costs for Personnel")
    phase1_total_budget_travel: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Travel")
    phase1_total_budget_equipment: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Equipment")
    phase1_total_budget_other_publication_fees: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Other Publications")
    phase1_total_budget_other_conferences_workshops: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Other Conferences and workshops")
    phase1_total_budget_other_other: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Other Other")
    phase1_total_budget_other_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Total Other Direct Costs")
    phase1_total_budget_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Total Direct Costs")
    phase1_total_budget_subcontracting: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Subcontracting")
    phase1_total_budget_total_costs: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 1", "Total Costs")

    # Phase 2 budget fields
    phase2_total_budget_personnel_senior_staff: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Personnel Senior Staff")
    phase2_total_budget_personnel_postdocs: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Personnel Postdocs")
    phase2_total_budget_personnel_students: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Personnel Students")
    phase2_total_budget_personnel_other: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Personnel Other")
    phase2_total_budget_personnel_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Total Direct Costs for Personnel")
    phase2_total_budget_travel: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Travel")
    phase2_total_budget_equipment: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Equipment")
    phase2_total_budget_other_publication_fees: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Other Publications")
    phase2_total_budget_other_conferences_workshops: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Other Conferences and workshops")
    phase2_total_budget_other_other: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Other Other")
    phase2_total_budget_other_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Total Other Direct Costs")
    phase2_total_budget_total_direct: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Total Direct Costs")
    phase2_total_budget_subcontracting: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Subcontracting")
    phase2_total_budget_total_costs: FloatWithEvidence = budget_field("Budget Tables: Budget Phase 2", "Total Costs")

    class Config:
        use_enum_values = True


class ORDApplication(ORDMetadata, ORDBudget):
    """
    Unified ORD Application Schema: Core + Extended extraction in one schema.
    """

    class Config:
        use_enum_values = True


class ORDApplicationEstablish(ORDMetadata, ORDBudgetEstablish):
    """
    Two-phase budget variant of ORD Application.

    Uses ProjectInfoMixin for project fields and PhasedBudgetMixin for phase-specific budget fields.
    """

    class Config:
        use_enum_values = True
