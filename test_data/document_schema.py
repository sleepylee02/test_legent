import sys
import os
from openai import OpenAI
from collections import defaultdict
import json
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import UPSTAGE_API_KEY

client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1"
)


# === 1. Load and merge HTML content by page ===
page = "1-80"
file_name = f"data/parsed_negligence_ratio-{page}.json"
with open(file_name, "r", encoding="utf-8") as f:
    data = json.load(f)

elements = data.get("elements", [])
page_html_map = defaultdict(list)

for el in elements:
    page = el.get("page")
    html = el.get("content", {}).get("html", "")
    if page is not None and html:
        page_html_map[page].append(html)

merged_page_html = {page: "\n".join(htmls) for page, htmls in page_html_map.items()}


# === 2. Merge every two pages and prepare inputs ===
sorted_pages = sorted(merged_page_html.keys())
merged_blocks = []

for i in range(0, len(sorted_pages), 2):
    pages = sorted_pages[i:i+2]
    html_combined = "\n".join(merged_page_html[p] for p in pages if p in merged_page_html)
    merged_blocks.append({
        "merged_id": (i // 2) + 1,
        "html": html_combined,
        "pages": pages
    })

print(merged_blocks[0])


# === 3. Prepare shared schema === 
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "accident_case",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "대주제": {
                    "type": "string",
                    "description": "사고의 전체 대분류 주제. 예: '차대차 직진 대 직진 사고 - 사거리 교차로(상대 차량이 측면 방향에서 진입)'"
                    },
                "사고종류": {
                    "type": "string",
                    "description": "사고의 구체적 유형. 예: '한쪽 차량 신호위반 사고 (기본과실)'"
                    },
                "사례개요": {
                    "type": "object",
                    "description": "사건에 대한 개요 정보",
                    "properties": {
                        "심의번호": {
                            "type": "string",
                            "description": "사건 심의번호. 예: '2018-051544'"
                            },
                        "결정비율": {
                            "type": "string",
                            "description": "과실 결정 비율. 예: 'A(청구) : B(피청구) = 0 : 100'"
                            },
                        "사고내용": {
                            "type": "string",
                            "description": "사고의 상세 내용. 예: '신호기 있는 사거리 교차로에서 적색신호에 직진하던 피청구차량과 녹색신호에 직진하던 청구차량간의 충돌사고'"
                            },
                        "참고인정기준": {
                            "type": "string",
                            "description": "판단에 참조한 기준. 예: '신호기가 있는 교차로에서 신호는 양 차량 운전자가 신뢰하는 것으로, A차량은 B차량이 적색신호를 위반하여 직진할 것을 예상하고 주의해야 할 이유가 없으므로 B차량의 일방과실로 정한다. 적색 기본비율 A : B = 0 : 100'"
                            }
                            },
                    "required": ["심의번호", "결정비율", "사고내용", "참고인정기준"]
                        },
                "주장내용": {
                    "type": "object",
                    "description": "청구인과 피청구인의 주요 주장",
                    "properties": {
                        "청구인": {
                            "type": "string",
                            "description": "청구인의 주장. 예: '청구차량은 우측도로에서 녹색신호에 교차로를 직진으로 통과 중이고, 피청구차량은 좌측도로에서 적색신호에 교차로를 직진으로 통과 중이므로(신호위반), 과실도표 201도를 적용하여 피청구인 과실 100% 적용함이 타당함'"
                            },
                        "피청구인": {
                            "type": "string",
                            "description": "피청구인의 주장. 예: '피청구차량은 적색신호가 아닌 황색신호에 교차로 진입하였고, 양 차량의 손상부위를 고려하면 피청구차량이 교차로에 선진입하였으므로, 청구인 40%, 피청구인 60% 과실적용함이 타당함'"
                            }
                        },
                    "required": ["청구인", "피청구인"]
                    },
                "입증자료": {
                    "type": "string",
                    "description": "제시된 입증자료. 예: '교통사고사실확인원에 피청구차량의 신호위반(적색신호에 교차로 진입)으로 판단됨, 피청구차량 조수석 측면부 파손, 청구차량 전면부 파손'"
                    },
                "주요쟁점": {
                    "type": "string",
                    "description": "쟁점사항. 예: '적색신호 위반 여부 및 교차로 선진입 차량의 우선권 인정 여부'"
                    },
                "결정근거": {
                    "type": "string",
                    "description": "판단 근거. 예: '교통사고사실확인원에 피청구차량의 신호위반(적색신호에 직진 주행 중)으로 기재되어 있고, 피청구인이 주장하는 사실관계를 확인할 객관적인 증거는 없는 상태임'"
                    },
                "결정이유": {
                    "type": "string",
                    "description": "최종 결정 이유. 예: '교통사고사실확인원상 신호기 있는 사거리 교차로에서 피청구차량이 적색신호에 교차로를 직진하였고(신호 위반), 만약, 피청구차량이 황색신호에 교차로를 진입하였다고 하여도 청구차량이 신호에 따라 직진하였으므로, 녹색신호에 따라 교차로에 진입한 청구차량의 과실을 인정하기 어려움 청구차량 0% 피청구차량 100%'"
                    }
                },
            "required": ["대주제", "사고종류", "사례개요", "주장내용", "입증자료", "주요쟁점", "결정근거", "결정이유"]
            }
        }
    }
 

# === 4. Send each HTML block and get structured responses ===
results = []

for block in tqdm(merged_blocks, desc="🔄 Processing merged HTML blocks"):
    html_input = block["html"]
    messages = [
        {
            "role": "system",
            "content": "You are an expert in information extraction. Extract information from the given HTML representation of image and organize them into a clear and accurate JSON format."
        },
        {
            "role": "user",
            "content": f"HTML string: {html_input}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="solar-pro",
            messages=messages,
            response_format=response_format
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = {"error": str(e)}

    print(result)

    results.append({
        "merged_id": block["merged_id"],
        "pages": block["pages"],
        "response": result
    })
 
# === 5. Save the results ===

with open(f"data/extracted_accident_cases-{page}.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("🎉 All blocks processed. Output saved")