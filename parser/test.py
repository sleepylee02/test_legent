import base64
import json
from openai import OpenAI
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY

client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/information-extraction"
)
 
def encode_img_to_base64(img_path):
    with open(img_path, 'rb') as img_file:
        img_bytes = img_file.read()
        base64_data = base64.b64encode(img_bytes).decode('utf-8')
        return base64_data
 
# Read the image file and encode it to base64
img_path = "data/test.png"
base64_data = encode_img_to_base64(img_path)
 
 
# Information Extraction Request using the generated schema
extraction_response = client.chat.completions.create(
    model="information-extract",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_data}"}
                }
            ]
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "document_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "bank_name": {
                        "type": "string",
                        "description": "The name of bank in bank statement"
                    }
                },
                "required": ["bank_name"]
            }
        }
    }
)
 
print(extraction_response.choices[0].message.content)