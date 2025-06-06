"""
document_preprocessing.py
────────────────────────
• Orchestrates the preprocessing pipeline:
  1. DP_negligence_ratio.py: PDF to HTML/Text
  2. document_schema.py: Extract accident cases
  3. document_to_json.py: Parse and structure data
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import json
import sys
import os

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from preprocessing.utils.DP_negligence_ratio import parse_file as dp_parse
from preprocessing.utils.document_schema import process_file as schema_process
from preprocessing.utils.document_to_json import parse_file as json_parse

class DocumentPreprocessor:
    def __init__(self, page: str):
        self.page = page
        self.base_dir = Path("data/negligence_ratio")
        
        # Define paths
        self.pdf_path = self.base_dir / f"negligence_ratio-{page}.pdf"
        self.parsed_dir = Path("data/negligence_ratio_parsed")
        self.extracted_dir = Path("data/negligence_ratio_extracted")
        
        # Create directories if they don't exist
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
    async def process_document(self) -> Dict[str, List[str]]:
        """Process document through the entire preprocessing pipeline"""
        results = {
            "dp_parsed": [],
            "schema_processed": [],
            "json_parsed": []
        }
        
        try:
            # 1. PDF to HTML/Text (DP_negligence_ratio.py)
            print(f"\nProcessing PDF: {self.pdf_path}")
            dp_parse(self.page)
            results["dp_parsed"].extend([
                f"negligence_ratio-{self.page}_html.json",
                f"negligence_ratio-{self.page}_text.json"
            ])
            
            # 2. Extract accident cases (document_schema.py)
            print("\nExtracting accident cases...")
            for fmt in ["html", "text"]:
                schema_process(self.page, fmt)
                results["schema_processed"].append(
                    f"extracted_accident_cases-{self.page}_{fmt}.json"
                )
            
            # 3. Parse and structure data (document_to_json.py)
            print("\nParsing and structuring data...")
            for fmt in ["html", "text"]:
                json_parse(self.page, fmt)
                results["json_parsed"].append(
                    f"parsed_accident_cases-{self.page}_{fmt}.json"
                )
            
        except Exception as e:
            print(f"Error in preprocessing pipeline: {str(e)}")
            raise
            
        return results

async def main():
    # Example usage
    processor = DocumentPreprocessor(page="81-160")
    
    try:
        results = await processor.process_document()
        
        # Save processing results
        results_path = Path("data/negligence_ratio/preprocessing_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nPreprocessing complete! Results saved to {results_path}")
        
    except Exception as e:
        print(f"Preprocessing failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 