"""
document_preprocessing.py
────────────────────────
• Orchestrates the preprocessing pipeline:
  1. DP_negligence_ratio.py: PDF to HTML/Text
  2. document_schema.py: Extract accident cases
  3. document_to_json.py: Parse and structure data
"""

import os
import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from preprocessing.utils.DP_negligence_ratio import parse_file as parse_1
from preprocessing.utils.document_schema import process_file as schema_process
from preprocessing.utils.document_to_json import parse_file as json_parse

def process_document(pdf_path: str, page: str):
    """Process a single document through all preprocessing steps"""
    print(f"\nProcessing document: {pdf_path}")
    
    # 1. PDF to HTML/Text
    print("Step 1: Converting PDF to HTML/Text")
    parse_1(page)
    
    # 2. Schema processing
    print("\nStep 2: Schema processing")
    html_file = f"data/negligence_ratio_parsed/negligence_ratio-{page}_html.json"
    schema_file = f"data/negligence_ratio_parsed/negligence_ratio-{page}_schema.json"
    schema_process(html_file, schema_file)
    
    # 3. JSON processing
    print("\nStep 3: JSON processing")
    json_file = f"data/negligence_ratio_parsed/negligence_ratio-{page}_json.json"
    json_parse(schema_file, json_file)
    
    print(f"\n✅ Document processing completed: {pdf_path}")

def main():
    # Create output directory if it doesn't exist
    os.makedirs("data/negligence_ratio_parsed", exist_ok=True)
    
    # Process the document
    pdf_path = "data/negligence_ratio/negligence_ratio-1-80.pdf"
    process_document(pdf_path, "1-80")

if __name__ == "__main__":
    main() 