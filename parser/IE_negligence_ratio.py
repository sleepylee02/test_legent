import base64
import json
from openai import OpenAI
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY


# --- Init Upstage Clients ---
client_schema = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/information-extraction/schema-generation"
)

client_extract = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/information-extraction"
)

 
# --- Utility: PDF -> base64 ---
def encode_pdf_to_base64(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

 
# --- Main Workflow ---
pdf_path = "data/ilovepdf_merged_2-1-80.pdf"
base64_pdf = encode_pdf_to_base64(pdf_path)
image_url_obj = {
    "type": "image_url",
    "image_url": {"url": f"data:application/pdf;base64,{base64_pdf}"}
}


# --- 1. Get Schema ---
schema_response = client_schema.chat.completions.create(
    model="information-extract",
    messages=[{"role": "user", "content": [image_url_obj]}]
)
schema = json.loads(schema_response.choices[0].message.content)

# --- 2. Extract Information ---
extraction_response = client_extract.chat.completions.create(
    model="information-extract",
    messages=[{"role": "user", "content": [image_url_obj]}],
    response_format=schema
)

# --- Save result ---
result = json.loads(extraction_response.choices[0].message.content)
with open("data/extracted_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("✅ Extracted result saved to data/extracted_result.json")