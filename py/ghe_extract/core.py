#!/usr/bin/env python3
"""
LlamaCloud Data Extraction Core Module

This module provides generalized data extraction services using LlamaCloud
with any Pydantic schema and configuration.

Environment Variables:
    LLAMA_CLOUD_API_KEY: Required for authentication
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Type, Union, Any, Dict
import json
import pandas as pd
import time

from llama_cloud_services import LlamaExtract
from llama_cloud import ExtractConfig
from pydantic import BaseModel
import logging
from flatten_json import flatten
from .utils import convert_directory_to_csv, find_documents, filter_documents_by_pattern

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LlamaCloudExtractor:
    """Generalized LlamaCloud extraction service"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LlamaCloud extractor"""
        self.api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY environment variable is required")

        self.extractor = LlamaExtract(api_key=self.api_key)
        logger.info("LlamaCloud extractor initialized")

    def extract_from_document(self, document_path: Path, schema: Type[BaseModel], config: ExtractConfig) -> dict:
        """Extract data from a single document using LlamaCloud"""
        logger.info(f"Extracting data from: {document_path}")

        try:
            # Perform extraction
            result = self.extractor.extract(schema, config, str(document_path))

            # Return structured data with all available information
            extraction_result = {
                "document_path": str(document_path),
                "status": "success",
                "data": result.data.dict() if hasattr(result.data, 'dict') else result.data,
                "metadata": {
                    "schema_name": schema.__name__,
                    "extraction_mode": config.extraction_mode.value if hasattr(config.extraction_mode, 'value') else str(config.extraction_mode)
                }
            }

            # Add extraction metadata if available (contains citations, confidence scores, etc.)
            if hasattr(result, 'extraction_metadata'):
                extraction_result["extraction_metadata"] = result.extraction_metadata

            # Add other potentially useful attributes
            for attr in ['config', 'job_id', 'extraction_agent_id', 'created_at', 'updated_at']:
                if hasattr(result, attr):
                    value = getattr(result, attr)
                    # Convert datetime objects to strings for JSON serialization
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    # Convert config objects to dict if possible
                    elif hasattr(value, '__dict__'):
                        try:
                            value = value.__dict__
                        except:
                            value = str(value)
                    extraction_result[attr] = value

            logger.info(f"Successfully extracted data from {document_path}")
            return extraction_result

        except Exception as e:
            logger.error(f"Failed to extract from {document_path}: {str(e)}")
            return {
                "document_path": str(document_path),
                "status": "error",
                "error": str(e),
                "data": None
            }

    def create_output_structure(self, input_directory: str, output_base: str) -> str:
        """Create output directory structure mirroring the input directory"""
        input_path = Path(input_directory)
        input_dir_name = input_path.name
        output_dir = Path(output_base) / input_dir_name

        # Walk through input directory and create corresponding output structure
        for root, dirs, files in os.walk(input_directory):
            root_path = Path(root)
            relative_path = root_path.relative_to(input_path)
            output_subdir = output_dir / relative_path
            output_subdir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created output structure at: {output_dir}")
        return str(output_dir)

    def save_results(self, results: List[dict], output_dir: str, output_prefix: str, input_directory: str):
        """Save extraction results to JSON files in pre-created structure"""
        output_path = Path(output_dir)
        input_path = Path(input_directory)

        # Save individual results
        for result in results:
            doc_path = Path(result["document_path"])
            doc_name = doc_path.stem

            # Calculate relative path from input directory and save to same structure
            relative_path = doc_path.relative_to(input_path)
            output_file = output_path / relative_path.parent / f"{output_prefix}_{doc_name}_extraction.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved extraction result to: {output_file}")

        # Return basic extraction statistics
        summary = {
            "total_documents": len(results),
            "successful_extractions": len([r for r in results if r["status"] == "success"]),
            "failed_extractions": len([r for r in results if r["status"] == "error"])
        }

        return summary

    def _output_file_exists(self, doc_path: Path, output_dir: str, output_prefix: str, input_directory: str) -> bool:
        """Check if the output JSON file already exists for this document"""
        input_path = Path(input_directory)
        relative_path = doc_path.relative_to(input_path)
        output_file = Path(output_dir) / relative_path.parent / f"{output_prefix}_{doc_path.stem}_extraction.json"
        return output_file.exists()

    def extract_directory(
        self,
        directory: str,
        schema: Type[BaseModel],
        config: ExtractConfig,
        output_prefix: str = "extraction",
        output_dir: str = None,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        skip_existing: bool = True,
        output_base: str = "inst/extdata/raw"
    ) -> dict:
        """Extract data from all documents in a directory

        Returns:
            dict: Extraction summary with counts
        """
        logger.info(f"Starting LlamaCloud extraction for directory: {directory}")
        logger.info(f"Schema: {schema.__name__}")

        # Find and filter documents
        documents = find_documents(directory)
        filtered_documents = filter_documents_by_pattern(documents, include_patterns, exclude_patterns)

        if not filtered_documents:
            pattern_desc = f"include={include_patterns}, exclude={exclude_patterns}" if exclude_patterns else f"include={include_patterns}"
            logger.warning(f"No documents found with patterns {pattern_desc} in {directory}")
            return {"total_documents": 0, "successful_extractions": 0, "failed_extractions": 0}

        # Extract from each document with retry logic
        results = []
        failed_files = []

        for doc_path in filtered_documents:
            # Check if we should skip existing files
            if skip_existing and self._output_file_exists(doc_path, output_dir or self.create_output_structure(directory, output_base),
                                                          output_prefix, directory):
                logger.info(f"Skipping {doc_path} - output file already exists")
                continue

            max_retries = 3
            delays = [0, 2, 15]  # immediate, 2 seconds, 15 seconds

            success = False
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        delay = delays[min(attempt, len(delays) - 1)]
                        logger.info(f"Retry attempt {attempt} for {doc_path} after {delay}s delay")
                        time.sleep(delay)

                    result = self.extract_from_document(doc_path, schema, config)

                    if result["status"] == "success":
                        success = True
                        result["metadata"]["attempts"] = attempt + 1
                        results.append(result)
                        break
                    else:
                        if attempt == max_retries - 1:
                            logger.error(f"All {max_retries} attempts failed for {doc_path}")
                            results.append(result)
                            failed_files.append(str(doc_path))

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {doc_path}: {str(e)}")
                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} attempts failed for {doc_path}")
                        error_result = {
                            "document_path": str(doc_path),
                            "status": "error",
                            "error": str(e),
                            "data": None,
                            "attempts": max_retries
                        }
                        results.append(error_result)
                        failed_files.append(str(doc_path))

        # Log failed files for reprocessing
        if failed_files:
            failed_files_log = "failed_extractions.json"
            with open(failed_files_log, 'w') as f:
                json.dump(failed_files, f, indent=2)
            logger.error(f"Failed extractions saved to: {failed_files_log}")
            logger.error(f"Total failed files: {len(failed_files)}")

        # Create output structure and save results
        if output_dir is None:
            output_dir = self.create_output_structure(directory, output_base)

        summary = self.save_results(results, output_dir, output_prefix, directory)

        # Convert extracted JSONs to CSV automatically
        json_directory = str(Path(output_base) / Path(directory).name)
        file_pattern = f'{output_prefix}*.json'
        output_csv = str(Path(output_base) / f"{output_prefix}.csv")

        try:
            convert_directory_to_csv(
                json_directory=json_directory,
                output_csv=output_csv,
                file_pattern=file_pattern
            )
            logger.info(f"CSV conversion completed: {output_csv}")
        except Exception as e:
            logger.warning(f"CSV conversion failed: {str(e)}")

        logger.info(f"Extraction complete! {summary['successful_extractions']}/{summary['total_documents']} successful")
        return summary
