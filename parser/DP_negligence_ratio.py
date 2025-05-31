import requests
import sys
import os
import json
import time
from collections import defaultdict
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY

# === Configuration ===
filename = "data/negligence_ratio/negligence_ratio-1-80.pdf"
base_name = filename[22:-4]  # negligence_ratio/negligence_ratio-1-80
api_url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
files = {"document": open(filename, "rb")}
data = {"ocr": "force", "base64_encoding": "['table']", "model": "document-parse"}

# === 1. Send request to Upstage API ===
start_time = time.time()
print("started document parsing")

response = requests.post(api_url, headers=headers, files=files, data=data)
result = response.json()
elapsed_time = time.time() - start_time
print(f"⏱️ API call took {elapsed_time:.2f} seconds")

# === 2. Save full HTML-based JSON (raw result) ===
elements = result.get("elements", [])
page_html_map = defaultdict(list)

for el in elements:
    page = el.get("page")
    html = el.get("content", {}).get("html")
    if page is not None and html:
        page_html_map[int(page)].append(html)

# Merge HTML blocks by 2 pages
merged_html_blocks = []
sorted_pages = sorted(page_html_map.keys())

for i in tqdm(range(0, len(sorted_pages), 2), desc="🧩 Merging HTML Blocks"):
    block_html = []
    for p in sorted_pages[i:i+2]:
        block_html.extend(page_html_map[p])
    merged_html_blocks.append({
        "id": len(merged_html_blocks) + 1,
        "html": "\n".join(block_html)
    })

# Save merged HTML block only
merged_html_json_path = f"data/negligence_ratio_parsed/{base_name}_html.json"

with open(merged_html_json_path, "w", encoding="utf-8") as f:
    json.dump(merged_html_blocks, f, ensure_ascii=False, indent=2)

print(f"📦 Merged HTML blocks saved to {merged_html_json_path}")


# === 3. Merge every two pages and clean with BeautifulSoup ===
merged_text_blocks = []

for i in tqdm(range(0, len(sorted_pages), 2), desc="🧹 Merging + Cleaning"):
    block_html = []
    for p in sorted_pages[i:i+2]:
        block_html.extend(page_html_map[p])
    soup = BeautifulSoup("\n".join(block_html), "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)

    merged_text_blocks.append({
        "id": len(merged_text_blocks) + 1,
        "text": clean_text
    })

# === 4. Save merged clean text blocks to JSON ===
text_json_path = f"data/negligence_ratio_parsed/{base_name}_text.json"

with open(text_json_path, "w", encoding="utf-8") as f:
    json.dump(merged_text_blocks, f, ensure_ascii=False, indent=2)

print(f"✅ Cleaned text blocks saved to {text_json_path}")