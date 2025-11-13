"""
Simple Extraction Guidance Framework

Generates structured field descriptions for LLM extraction.
"""

from typing import List, Optional


def extraction_guide(
    table: Optional[str] = None,
    variable: Optional[str] = None,
    section: Optional[str] = None,
    format_spec: Optional[str] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    description: Optional[str] = None,
    options: Optional[List[str]] = None
) -> dict:
    """
    Generate extraction guidance for LLM field descriptions.

    Args:
        table: Table name (generates "From 'table' table: 'variable'")
        variable: Variable name (used with table)
        section: Section name (generates "From 'section' section")
        format_spec: Expected output format (e.g., "DD.MM.YYYY" becomes "DD.MM.YYYY format")
        include: List of what to include (e.g., ["Project title"] becomes "Project title only")
        exclude: List of what to exclude from extraction
        description: Custom description text (used instead of generated source description)
        options: List of possible values (e.g., ["ETH Zürich", "EPFL", "PSI"])

    Returns:
        Dict with 'description' key containing the generated guidance
    """
    description_parts = []

    # Use custom description or generate source description
    if description:
        description_parts.append(description)
    elif table and variable:
        description_parts.append(f"From '{table}' table: '{variable}'")
    elif section:
        description_parts.append(f"From '{section}' section")

    if format_spec:
        description_parts.append(f"{format_spec} format")

    if include:
        include_text = ", ".join(include)
        description_parts.append(f"{include_text} only")

    if exclude:
        exclude_items = ", ".join(exclude)
        description_parts.append(f"Do not include {exclude_items}")

    if options:
        options_text = ", ".join(options)
        description_parts.append(f"({options_text})")

    return {"description": ". ".join(description_parts)}