import requests
import sys
import os
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY

filename = "data/negligence_ratio-1-80.pdf"  
 
url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
files = {"document": open(filename, "rb")}
data = {"ocr": "force", 
        "base64_encoding": "['table']", 
        "model": "document-parse"}

start_time = time.time()

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"⏱️ API call took {elapsed_time:.2f} seconds")


## json output
json_output_path = f"data/parsed_{filename[5:-4]}.json"
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"📦 Full JSON saved to {json_output_path}")

# text output
elements = result.get("elements", [])
plain_texts = []

for el in tqdm(elements, desc="🔍 Extracting text"):
    html = el.get("content", {}).get("html")
    if html:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        plain_texts.append(text)

# 전체 텍스트 연결
final_text = "\n\n".join(plain_texts)
output_path = f"data/parsed_{filename[5:-4]}.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"✅ Extracted {len(plain_texts)} elements and saved to {output_path}")