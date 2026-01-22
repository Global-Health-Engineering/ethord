#!/usr/bin/env python3
"""
Diff Analysis Script for ethord CSV files

Compares CSV files in inst/extdata/ between the current branch and main branch.
Creates individual diff files for each CSV and a summary file.

Usage:
    python diff/diff_analysis.py

Output:
    - diff/<filename>_diff.csv: Detailed changes for each file
    - diff/diff_summary.csv: Summary of changes per file
"""

import pandas as pd
import subprocess
from io import StringIO
from pathlib import Path

# Get list of CSV files to compare
CSV_FILES = [
    "application_budget.csv",
    "application_ethics.csv",
    "application_metadata.csv",
    "application_metadata_applicants.csv",
    "application_metadata_keywords.csv",
    "application_metadata_work_packages.csv",
    "project_mapping.csv",
    "report_metadata.csv",
    "report_metadata_coapplicants.csv",
    "report_output.csv"
]

DIFF_DIR = Path("diff")
EXTDATA_DIR = Path("inst/extdata")


def get_file_from_main(file_path: str) -> pd.DataFrame:
    """Get a CSV file from the main branch."""
    main_content = subprocess.check_output(
        ["git", "show", f"main:{file_path}"],
        stderr=subprocess.DEVNULL
    ).decode('utf-8')
    return pd.read_csv(StringIO(main_content))


def compare_dataframes(df_main: pd.DataFrame, df_current: pd.DataFrame) -> list:
    """Compare two dataframes and return a list of changes."""
    changes = []

    # Find common columns
    common_cols = set(df_main.columns) & set(df_current.columns)
    new_cols = set(df_current.columns) - set(df_main.columns)
    removed_cols = set(df_main.columns) - set(df_current.columns)

    # Record new columns
    for col in new_cols:
        dtype = "numeric" if pd.api.types.is_numeric_dtype(df_current[col]) else "text"
        changes.append({
            "change_type": "new_column",
            "column": col,
            "row": "N/A",
            "row_number_main": "N/A",
            "row_number_current": "N/A",
            "old_value": "N/A",
            "new_value": f"[column added with {len(df_current)} values]",
            "data_type": dtype
        })

    # Record removed columns
    for col in removed_cols:
        dtype = "numeric" if pd.api.types.is_numeric_dtype(df_main[col]) else "text"
        changes.append({
            "change_type": "removed_column",
            "column": col,
            "row": "N/A",
            "row_number_main": "N/A",
            "row_number_current": "N/A",
            "old_value": f"[column removed with {len(df_main)} values]",
            "new_value": "N/A",
            "data_type": dtype
        })

    # Find key column for row matching
    if 'project_id' in common_cols:
        key_col = 'project_id'
    elif len(common_cols) > 0:
        key_col = list(common_cols)[0]
    else:
        return changes

    # Add row numbers (1-indexed, +2 for header row)
    df_main = df_main.copy()
    df_current = df_current.copy()
    df_main['_row_num'] = range(2, len(df_main) + 2)
    df_current['_row_num'] = range(2, len(df_current) + 2)

    # Create unique row identifier by adding occurrence count for duplicates
    df_main['_occurrence'] = df_main.groupby(key_col).cumcount()
    df_current['_occurrence'] = df_current.groupby(key_col).cumcount()

    # Create composite key
    df_main['_composite_key'] = df_main[key_col].astype(str) + '_' + df_main['_occurrence'].astype(str)
    df_current['_composite_key'] = df_current[key_col].astype(str) + '_' + df_current['_occurrence'].astype(str)

    # Create lookup dictionaries
    main_rows = {row['_composite_key']: row for _, row in df_main.iterrows()}
    current_rows = {row['_composite_key']: row for _, row in df_current.iterrows()}

    main_keys = set(main_rows.keys())
    current_keys = set(current_rows.keys())

    new_rows = current_keys - main_keys
    removed_rows = main_keys - current_keys
    common_rows = main_keys & current_keys

    # Record new rows
    for comp_key in new_rows:
        row = current_rows[comp_key]
        changes.append({
            "change_type": "new_row",
            "column": key_col,
            "row": str(row[key_col]),
            "row_number_main": "N/A",
            "row_number_current": row['_row_num'],
            "old_value": "N/A",
            "new_value": "[new row]",
            "data_type": "text"
        })

    # Record removed rows
    for comp_key in removed_rows:
        row = main_rows[comp_key]
        changes.append({
            "change_type": "removed_row",
            "column": key_col,
            "row": str(row[key_col]),
            "row_number_main": row['_row_num'],
            "row_number_current": "N/A",
            "old_value": "[row removed]",
            "new_value": "N/A",
            "data_type": "text"
        })

    # Compare values in common rows and columns
    for comp_key in common_rows:
        main_row = main_rows[comp_key]
        current_row = current_rows[comp_key]

        for col in common_cols:
            if col == key_col:
                continue
            try:
                old_val = main_row[col]
                new_val = current_row[col]

                # Handle NaN comparison
                old_is_na = pd.isna(old_val)
                new_is_na = pd.isna(new_val)

                # Both NA - no change
                if old_is_na and new_is_na:
                    continue

                # Check if values are numeric
                def is_numeric(val):
                    if pd.isna(val):
                        return False
                    try:
                        float(val)
                        return True
                    except (ValueError, TypeError):
                        return False

                old_is_numeric = is_numeric(old_val)
                new_is_numeric = is_numeric(new_val)

                # For numeric values, compare as numbers
                if old_is_numeric and new_is_numeric:
                    if float(old_val) == float(new_val):
                        continue
                # Handle NA vs 0 as equivalent
                elif (old_is_na and new_is_numeric and float(new_val) == 0) or \
                     (new_is_na and old_is_numeric and float(old_val) == 0):
                    continue
                # For non-numeric, compare as strings
                elif not old_is_na and not new_is_na and str(old_val) == str(new_val):
                    continue

                # If we get here, there's a real change
                if old_is_na != new_is_na or str(old_val) != str(new_val):
                    dtype = "numeric" if pd.api.types.is_numeric_dtype(df_current[col]) else "text"
                    changes.append({
                        "change_type": "value_changed",
                        "column": col,
                        "row": str(main_row[key_col]),
                        "row_number_main": main_row['_row_num'],
                        "row_number_current": current_row['_row_num'],
                        "old_value": str(old_val) if not old_is_na else "NA",
                        "new_value": str(new_val) if not new_is_na else "NA",
                        "data_type": dtype
                    })
            except Exception as e:
                print(f"Error comparing {col} for {comp_key}: {e}")

    return changes


def main():
    """Run the diff analysis."""
    DIFF_DIR.mkdir(exist_ok=True)
    summary_data = []

    for csv_file in CSV_FILES:
        file_path = EXTDATA_DIR / csv_file

        # Get the file from main branch
        try:
            df_main = get_file_from_main(str(file_path))
        except Exception as e:
            print(f"Could not get {csv_file} from main: {e}")
            continue

        # Read current file
        try:
            df_current = pd.read_csv(file_path)
        except Exception as e:
            print(f"Could not read current {csv_file}: {e}")
            continue

        # Compare dataframes
        changes = compare_dataframes(df_main, df_current)

        # Save diff file
        diff_file = DIFF_DIR / csv_file.replace('.csv', '_diff.csv')
        if changes:
            diff_df = pd.DataFrame(changes)
            diff_df = diff_df[[
                "change_type", "column", "row", "row_number_main",
                "row_number_current", "old_value", "new_value", "data_type"
            ]]
            diff_df.to_csv(diff_file, index=False)
            print(f"{csv_file}: {len(changes)} changes")
        else:
            pd.DataFrame(columns=[
                "change_type", "column", "row", "row_number_main",
                "row_number_current", "old_value", "new_value", "data_type"
            ]).to_csv(diff_file, index=False)
            print(f"{csv_file}: 0 changes")

        summary_data.append({"file": csv_file, "number_of_changes": len(changes)})

    # Save summary
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(DIFF_DIR / "diff_summary.csv", index=False)
    print(f"\nSummary saved to {DIFF_DIR}/diff_summary.csv")
    print("\n" + summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
