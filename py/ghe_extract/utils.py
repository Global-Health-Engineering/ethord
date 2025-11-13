import json
import pandas as pd
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional, List, Union
from flatten_json import flatten
import logging

logger = logging.getLogger(__name__)

def flatten_to_long(df):
    """Remove first _<int> from columns, create long format with <prefix>_id"""
    pattern = re.compile(r'(.*)_(\d+)(.*)')
    col_map, non_indexed, groups = {}, [], defaultdict(set)

    for col in df.columns:
        m = pattern.match(col)
        if m:
            prefix, idx, suffix = m.group(1), int(m.group(2)), m.group(3)
            col_map[col] = (prefix, idx, prefix + suffix)
            groups[prefix].add(idx)
        else:
            non_indexed.append(col)

    if not col_map:
        return df

    all_rows = []

    # Process each row in the DataFrame
    for record_idx in range(len(df)):
        rows_data = defaultdict(lambda: defaultdict(dict))
        for old_col, (prefix, idx, new_col) in col_map.items():
            rows_data[prefix][idx][new_col] = df[old_col].iloc[record_idx]

        # Create long format rows for this record
        for prefix in sorted(groups):
            for idx in sorted(groups[prefix]):
                row = df[non_indexed].iloc[record_idx].to_dict()
                row.update(rows_data[prefix][idx])
                row[f'{prefix}_id'] = idx + 1
                all_rows.append(row)

    result = pd.DataFrame(all_rows)
    indexed_cols = list({new_col for _, _, new_col in col_map.values()})
    return result.dropna(subset=indexed_cols, how='all')


def find_documents(directory: str, file_types: List[str] = None) -> List[Path]:
    """Find documents in the specified directory"""
    if file_types is None:
        file_types = ['pdf', 'docx', 'md']

    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    documents = []
    for file_type in file_types:
        documents.extend(list(directory_path.rglob(f"*.{file_type}")))

    logger.info(f"Found {len(documents)} documents in {directory}")
    return documents

def filter_documents_by_pattern(
    documents: List[Path],
    include_patterns: Optional[Union[str, List[str]]] = None,
    exclude_patterns: Optional[Union[str, List[str]]] = None
) -> List[Path]:
    """Filter documents based on include/exclude patterns in file path"""
    if include_patterns is None:
        return documents

    # Handle both single string and list of strings for include patterns
    if isinstance(include_patterns, str):
        include_list = [include_patterns]
    else:
        include_list = include_patterns

    # Handle exclude patterns
    if exclude_patterns is None:
        exclude_list = []
    elif isinstance(exclude_patterns, str):
        exclude_list = [exclude_patterns]
    else:
        exclude_list = exclude_patterns

    def matches_criteria(doc_path: Path) -> bool:
        doc_str = str(doc_path).lower()

        # Must match ALL include patterns
        includes_match = all(pattern.lower() in doc_str for pattern in include_list)

        # Must NOT match ANY exclude patterns
        excludes_match = any(pattern.lower() in doc_str for pattern in exclude_list) if exclude_list else False

        return includes_match and not excludes_match

    filtered = [doc for doc in documents if matches_criteria(doc)]

    # Build descriptive log message
    include_desc = include_patterns if isinstance(include_patterns, str) else include_list
    if exclude_list:
        exclude_desc = exclude_patterns if isinstance(exclude_patterns, str) else exclude_list
        logger.info(f"Filtered to {len(filtered)} documents with include={include_desc}, exclude={exclude_desc}")
    else:
        logger.info(f"Filtered to {len(filtered)} documents with include={include_desc}")

    return filtered

def convert_json_to_csv(
    json_files: Union[str, List[str]],
    output_csv: str,
    to_wide = True,
) -> pd.DataFrame:
    """
    Convert extraction JSON files to CSV by flattening to wide format first,
    then concatenating, then converting to long format.

    Args:
        json_files: Single JSON file path or list of JSON file paths
        output_csv: Output CSV file path

    Returns:
        pandas.DataFrame: The converted data
    """
    logger.info("Converting JSON extractions to CSV")

    if isinstance(json_files, str):
        json_files = [json_files]

    all_data = []

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            extraction_data = json.load(f)

        if extraction_data.get("status") != "success":
            logger.warning(f"Skipping failed extraction: {json_file}")
            continue

        # Flatten each JSON record to wide format using flatten_json
        flattened_data = flatten(extraction_data, separator='_')
        all_data.append(flattened_data)

    # Create DataFrame from all flattened wide data
    df = pd.DataFrame(all_data)
    
    if not to_wide:
        # Apply flatten_to_long transformation to the combined wide DataFrame
        df = flatten_to_long(df)

    # Save to CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    logger.info(f"Saved CSV with {len(df)} rows to: {output_csv}")

    return df

def convert_directory_to_csv(
    json_directory: str,
    output_csv: str,
    file_pattern: str = "*_extraction.json",
    to_wide = True
) -> pd.DataFrame:
    """
    Convert all JSON extraction files in a directory to CSV.

    Args:
        json_directory: Directory containing JSON extraction files
        output_csv: Output CSV file path
        file_pattern: Glob pattern to match JSON files

    Returns:
        pandas.DataFrame: The converted data
    """
    json_dir = Path(json_directory)
    json_files = list(json_dir.rglob(file_pattern))

    if not json_files:
        logger.warning(f"No JSON files found matching pattern '{file_pattern}' in {json_directory}")
        return pd.DataFrame()

    logger.info(f"Found {len(json_files)} JSON files to convert")

    return convert_json_to_csv([str(f) for f in json_files], output_csv, to_wide = to_wide)
