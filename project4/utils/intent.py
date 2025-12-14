from typing import Dict, Tuple

def parse_intent_and_constraints(text: str) -> Tuple[str, Dict]:
    t = (text or "").strip()
    lower = t.lower()

    # intent
    # curation: 소개/분석/해석/설명/어때/볼까말까/결말스포X 등
    curation_keywords = ["소개", "분석", "해석", "설명", "어때", "볼까", "볼지", "큐레이션", "리뷰", "평"]
    recommend_keywords = ["추천", "비슷한", "같은", "골라", "뭐 볼", "뭐볼", "추천해", "추천좀"]

    intent = "RECOMMEND"
    if any(k in t for k in curation_keywords) and not any(k in t for k in recommend_keywords):
        intent = "CURATE"
    if any(k in t for k in recommend_keywords):
        intent = "RECOMMEND"

    constraints: Dict = {}
    # 간단한 제약 추출(확장 가능)
    if "크리스마스" in t:
        constraints["mood"] = "christmas"
    if "로맨스" in t or "멜로" in t:
        constraints["genre"] = "romance"
    if "공포" in t or "호러" in t:
        constraints["genre"] = "horror"

    return intent, constraints
