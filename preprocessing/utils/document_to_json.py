"""
document_to_json.py
──────────────────
• input : data/negligence_ratio_extracted/extracted_accident_cases-{page}_{fmt}.json
          (원본 크롤링/추출 결과)
• output: data/negligence_ratio_extracted/parsed_accident_cases-{page}_{fmt}.json
          (response 필드를 정식 JSON 으로 변환‧동시에 원본도 보존)
• 실패   레코드는 debug_bad_records/ 아래 *.txt 로 남겨서 눈으로 확인
"""

import argparse
import html
import json
import pathlib
import re
from typing import Optional

# ────────────────────────────────────────────────────────────────────────────
# ①  오류를 일으키는 패턴만 안전하게 정규화
CTRL_RE = re.compile(r'[\x00-\x1F\x7F]')          # 제어 문자
ORPHAN_QUOTE_RE = re.compile(r'(?<!\\)"')         # 백슬래시로 escape 안 된 "

def _normalize_json_like(text: str) -> str:
    """문자열 → JSON 파싱 전 1차 정규화"""
    text = html.unescape(text)
    text = CTRL_RE.sub("", text)
    text = ORPHAN_QUOTE_RE.sub(r"\\u0022", text)  # 고아 따옴표 → 유니코드 이스케이프

    # 중괄호 개수 맞추기 (끝이 잘린 경우)
    diff = text.count("{") - text.count("}")
    if diff > 0:
        text += "}" * diff
    return text

def _safe_load(text: str, rec_id: int, dump_dir: pathlib.Path) -> Optional[dict]:
    """정규화 후에도 안 되면 raw 를 파일로 떨궈 두고 None 반환"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(_normalize_json_like(text))
    except json.JSONDecodeError:
        dump_dir.mkdir(parents=True, exist_ok=True)
        (dump_dir / f"bad_{rec_id}.txt").write_text(text, encoding="utf-8")
        print(f"[FAIL] merged_id {rec_id}: 복구 실패 → raw 저장")
        return None
# ────────────────────────────────────────────────────────────────────────────


def parse_file(page: str, fmt: str) -> None:
    in_path  = pathlib.Path(f"data/negligence_ratio_extracted/extracted_accident_cases-{page}_{fmt}.json")
    out_path = pathlib.Path(f"data/negligence_ratio_json/json_accident_cases-{page}_{fmt}.json")
    dump_dir = pathlib.Path("data/negligence_ratio_json/debug_bad_records")

    raw_data = json.loads(in_path.read_text(encoding="utf-8"))
    parsed_records = []

    for rec in raw_data:
        rec_id = rec.get("merged_id", -1)
        parsed_resp = _safe_load(rec.get("response", ""), rec_id, dump_dir)
        if parsed_resp is None:
            continue
        # 원본 구조를 보존하면서 'parsed_response' 필드만 추가
        parsed_records.append({**rec, "parsed_response": parsed_resp})

    out_path.write_text(json.dumps(parsed_records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] {len(parsed_records)}개 레코드 파싱 완료 → {out_path}")
    if dump_dir.exists() and any(dump_dir.iterdir()):
        print(f"[INFO] 일부 레코드는 수동 확인 필요 → {dump_dir}/")

# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 직접 지정 (예: extracted_accident_cases-1-80_html.json)
    page = "1-80"
    fmt = "html"

    parse_file(page, fmt)