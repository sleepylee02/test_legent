import json
from bs4 import BeautifulSoup

# JSON 결과 불러오기
file_name = "data/parsed_negligence_ratio-1-80.json"

with open(file_name, "r", encoding="utf-8") as f:
    result = json.load(f)

elements = result.get("elements", [])

for target_page in range(71, 73):
    # target_page에 해당하는 요소만 필터링하고, 불필요한 필드 제거
    filtered_elements = []
    for el in elements:
        if el.get("page") == target_page:
            content = el.get("content", {})
            html = content.get("html", "")
            # BeautifulSoup으로 텍스트 추출
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            filtered_el = {
                "category": el.get("category"),
                "content": {
                    "html": html,
                }
            }

            filtered_elements.append(filtered_el)

    # 결과는 elements만 저장
    with open(f"data/page_{target_page}.json", "w", encoding="utf-8") as f:
        json.dump(filtered_elements, f, ensure_ascii=False, indent=2)