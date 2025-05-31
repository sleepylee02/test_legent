import sys
import os
from openai import OpenAI
from collections import defaultdict
import json
from tqdm import tqdm
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)  # 또는 직접 입력

# === Load few-shot prompt ===
with open("parser/reinforcement_fewshot.txt", "r", encoding="utf-8") as f:
    fewshot_prompt = f.read().strip()

# === Load Data ===
page = "1-80"
with open(f"data/negligence_ratio_extracted/extracted_accident_cases-{page}_html.json", encoding="utf-8") as f:
    html_data = {item["merged_id"]: item["response"] for item in json.load(f)}

with open(f"data/negligence_ratio_extracted/extracted_accident_cases-{page}_html.json", encoding="utf-8") as f:
    text_data = {item["merged_id"]: item["response"] for item in json.load(f)}

response_format= {
    "type": "json_schema",
    "json_schema": {
            "name": "accident_case",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "대주제": {"type": "string"},
                    "사고종류": {"type": "string"},
                    "사례개요": {
                        "type": "object",
                        "properties": {
                            "심의번호": {"type": "string"},
                            "결정비율": {"type": "string"},
                            "사고내용": {"type": "string"},
                            "참고인정기준": {"type": "string"}
                        },
                        "required": ["심의번호", "결정비율", "사고내용", "참고인정기준"],
                        "additionalProperties": False
                    },
                    "주장내용": {
                        "type": "object",
                        "properties" : {
                            "청구인": {"type": "string"},
                            "피청구인": {"type": "string"}
                        },
                        "required": ["청구인", "피청구인"],
                        "additionalProperties": False

                    },
                    "입증자료": {"type": "string"},
                    "주요쟁점": {"type": "string"},
                    "결정근거": {"type": "string"},
                    "결정이유": {"type": "string"}
                },
            "required": ["대주제", "사고종류", "사례개요", "주장내용", "입증자료", "주요쟁점", "결정근거", "결정이유"],
            "additionalProperties": False
            }
        }
    }

# === LLM-based Field-Level Merger ===
def merge_with_llm(a_json, b_json, fewshot: str):
    user_prompt = f"""
You will be given two structured JSON outputs (A and B), extracted from the same legal case. 
You also have multiple examples that demonstrate the correct output format and style.

Your task is to select, for each field, the better version between A and B. Use the few-shot examples to decide which version better matches the expected structure, terminology, and level of detail. Do NOT paraphrase, rewrite, or modify any content—only choose the more appropriate field from A or B.

If only one output contains a value, use that. If both exist, prefer the one that better follows the few-shot format.

Always return a valid JSON that follows the schema. Do not include explanations or formatting outside of the JSON.

### Examples:
{fewshot}

### Output A:
{json.dumps(a_json)}

### Output B:
{json.dumps(b_json)}

### Final Answer:
"""
    try:
        response = client.chat.completions.create(
            model="o3-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert in comparing structured legal outputs.
                    Your job is to choose which JSON field better matches the desired few-shot example format.
                    Never invent or rewrite. Just select between A or B per field.
                    """
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format=response_format
        )
        content = response.choices[0].message.content.strip()
        print(content)
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}



# === Run and save ===
merged_results = []

for mid in tqdm(html_data):
    html_json = html_data.get(mid)
    text_json = text_data.get(mid)
    try:
        html_json_clean = html_json.replace('\t', '') if isinstance(html_json, str) else html_json
        text_json_clean = text_json.replace('\t', '') if isinstance(text_json, str) else text_json

        html_parsed = json.loads(html_json_clean) if isinstance(html_json_clean, str) else html_json_clean
        text_parsed = json.loads(text_json_clean) if isinstance(text_json_clean, str) else text_json_clean

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error at id={mid}: {e}")
        sys.exit(1)
    
    merged = merge_with_llm(html_parsed, text_parsed, fewshot_prompt)
    merged_results.append({"merged_id": mid, "response": merged})

# === Save
with open(f"data/negligence_ratio_extracted/extracted_accident_cases-{page}_reinforced.json", "w", encoding="utf-8") as f:
    json.dump(merged_results, f, ensure_ascii=False, indent=2)

print("✅ Merge completed")

