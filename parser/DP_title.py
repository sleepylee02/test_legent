import requests
import sys
import os
import json
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY

filename = "data/title.pdf"  
print(filename[5:])
url = "https://api.upstage.ai/v1/document-digitization"

headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
files = {"document": open(filename, "rb")}
data = {"ocr": "force", "base64_encoding": "['table']", "model": "document-parse"}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

elements = result.get("elements", [])
plain_texts = []

for el in elements:
    html = el.get("content", {}).get("html")
    if html:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        plain_texts.append(text)

# 전체 텍스트 연결
final_text = "\n\n".join(plain_texts)

# 파일 저장 경로
output_path = "data/title_extracted.txt"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"✅ Extracted {len(plain_texts)} elements and saved to {output_path}")