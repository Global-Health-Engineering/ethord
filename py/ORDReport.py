from typing import List, Literal
from pydantic import BaseModel, Field
from ghe_extract.extraction_guide import extraction_guide

# Configuration
USE_EVIDENCE = False

# Conditional type imports/assignments
if USE_EVIDENCE:
    from ghe_extract.WithEvidence import StringWithEvidence, IntWithEvidence, LiteralWithEvidence
else:
    # Standard type aliases when not using evidence
    StringWithEvidence = str
    IntWithEvidence = int

    def LiteralWithEvidence(*options):
        """Factory function to create Literal types when not using evidence"""
        return Literal[options] if len(options) > 1 else Literal[options[0]]


class OutputItem(BaseModel):
    """Output category from ORD report table - mirrors the actual table structure"""
    quantity: IntWithEvidence = Field(**extraction_guide(
        variable="#",
        description="Total number of outputs for this Item"
    ))
    descriptions: List[StringWithEvidence] = Field(**extraction_guide(
        variable="Further details / description / explanation",
        format_spec="Comma-separated list",
        include=["all outputs descriptions reported"],
        exclude=["URLs"]
    ))
    urls: List[StringWithEvidence] = Field(**extraction_guide(
        variable="Further details / description / explanation",
        format_spec="Comma-separated list",
        include=["all output URLs reported"],
        exclude=["descriptions"]
    ))

    class Config:
        use_enum_values = True

class Coapplicant(BaseModel):
    """Output category from ORD report table - mirrors the actual table structure"""
    name: StringWithEvidence = Field(**extraction_guide(
        variable="Co-applicant",
        include=["Full name of co-applicant"]
    ))
    function: StringWithEvidence = Field(**extraction_guide(
        variable="Function",
        include=["Function of co-applicant"]
    ))
    institution: StringWithEvidence = Field(**extraction_guide(
        variable="Institution (incl. department/laboratory)",
        include=["Institution of co-applicant acronym"]
    ))
    roles_and_main_tasks: StringWithEvidence = Field(**extraction_guide(
        variable="Roles & main tasks within ORD project",
        include=["Role of co-applicant within ORD project"]
    ))

    class Config:
        use_enum_values = True
 

class ORDReportMetadata(BaseModel):
    """
    ORD Report Metadata Schema: Project identification and general information.

    Focuses on extracting:
    - Project basic information
    - Main applicant details
    - Report metadata
    - Co-applicants
    """

    # Project identification
    project_title: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Project title"
    ))
    explore_call_number: IntWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Explore call number",
        format_spec="1st = 1, 2nd = 2, 3rd = 3, 4th = 4, ..."
    ))
    project_starting_and_end_date: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Project starting & end date"
    ))
    main_applicant_responsible_for_project: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Main applicant responsible for project",
        exclude=["titles"],
        include="details of one person, the main applicant"
    ))
    function: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Function",
        include="details of one person, the main applicant"
    ))
    laboratory_department: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Laboratory (and/or Department)",
        include="details of one person, the main applicant"
    ))
    institution_of_main_applicant: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Institution of main applicant",
        include="details of one person, the main applicant"
    ))
    report: LiteralWithEvidence("Final", "Intermediate", "other") = Field(**extraction_guide(
        table="General information",
        variable="Report type"
    ))
    reporting_period: StringWithEvidence = Field(**extraction_guide(
        table="General information",
        variable="Reporting period (MM/YY to MM/YY)"
    ))
    coapplicants: List[Coapplicant] = Field(**extraction_guide(
        table="Co-applicant(s) involved in the project",
        format_spec="Comma-separated list",
        include=["all co-applicants"]
    ))

    class Config:
        use_enum_values = True


class ORDReportOutput(BaseModel):
    """
    ORD Report Output Schema: Extract project outputs from the "List of Outputs" table.

    Simplified schema for reliable list extraction of all 15 categories.
    ALL categories must be present in output (empty lists if no data).
    """

    # Category 1: Technical Infrastructure
    websites_platforms: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New or enhanced website(s), web interface, platform(s) and/or infrastructure' category"
    ))

    # Category 2: Data Repositories
    repositories_catalogues: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New or enhanced repositories and/or catalogs' category"
    ))

    # Category 3: Datasets
    datasets_databases: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New or enhanced datasets and/or databases' category"
    ))

    # Category 4: Software & Tools
    software_tools: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New or enhanced software, hardware, prototypes and/or other tools' category"
    ))

    # Category 5: Standards & Guidelines
    models_standards: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New or enhanced models, standards, guidelines, workflows, benchmarks, protocols and/or best practice' category"
    ))

    # Category 6: Workshops
    workshops: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Scientific workshops organized as part of the project' category"
    ))

    # Category 7: Training
    training_events: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Training and educational events and/or resources directly related to the project' category"
    ))

    # Category 8: Publications
    publications: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Scientific publications directly related to project (whether in progress, submitted, accepted or published)' category"
    ))

    # Category 9: Presentations
    presentations: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Presentations (e.g. conferences, poster, etc.) directly related to the project' category"
    ))

    # Category 10: Outreach
    outreach_activities: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Outreach, dissemination, communications or networking events and/or activities directly related to the project' category"
    ))

    # Category 11: Intellectual Property
    patents_ip: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Patents, patents applications or other intellectual property directly related to the project' category"
    ))

    # Category 12: Academic Collaborations
    new_collaborations: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New collaborations (except with industrial partners)' category"
    ))

    # Category 13: Industry Partnerships
    industrial_collaborations: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'New collaborations and/or contracts with industrial partners' category"
    ))

    # Category 14: Community Impact
    estimated_users: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Estimated number of users within the community benefiting from enhanced ORD practices' category"
    ))

    # Category 15: Other Outputs
    other_outputs: OutputItem = Field(**extraction_guide(
        table="List of Outputs",
        description="extract quantity, all descriptions, and all urls for 'Item': 'Other outputs (please specify)' category"
    ))

    class Config:
        use_enum_values = True


class ORDReport(ORDReportMetadata, ORDReportOutput):
    """
    Unified ORD Report Schema: Metadata + Output extraction in one schema.
    """

    class Config:
        use_enum_values = True
