from typing import Dict, List
from curators.base import CuratorBot, safe_json_loads
from curators.prompts import (
    CINEPHILE_SYSTEM, COMMON_OUTPUT_RULES, CONVERSATION_RULES, NEXT_TURN_SUGGESTIONS
)
from utils.kobis import KobisClient

class CinephileBot(CuratorBot):
    def __init__(self, kobis: KobisClient):
        super().__init__("🎬 영화덕후", CINEPHILE_SYSTEM, kobis)

    def think_recommend(self, user_input: str, constraints: Dict) -> List[Dict]:
        # 배우 언급이 있으면 people API로 필모 힌트
        people_hint = []
        try:
            # 아주 단순: “OOO 영화” 패턴을 잡아 people 검색 힌트로만 사용
            tokens = user_input.replace("배우", " ").replace("출연", " ").split()
            if tokens:
                candidate = tokens[0]
                pdata = self.kobis.search_people_list(peopleNm=candidate, itemPerPage=5)
                plist = pdata.get("peopleListResult", {}).get("peopleList", []) or []
                if plist:
                    people_hint = [p.get("filmoNames") for p in plist[:2] if p.get("filmoNames")]
        except Exception:
            people_hint = []

        prompt = f"""
사용자 요청: {user_input}
덕후 관점에서 추천 영화 1~2편만 고르라.
가능하면 아래 필모 힌트를 참고해도 된다(없어도 됨): {people_hint}

반드시 JSON 배열로만 출력:
[
  {{"title":"영화제목", "why":"덕후스러운 이유(짧게)", "risk":"취향탈 요소(짧게)"}},
  ...
]
"""
        raw = self.llm(prompt, temperature=0.95)
        data = safe_json_loads(raw)
        if isinstance(data, list) and data:
            out = []
            for it in data[:2]:
                if isinstance(it, dict) and it.get("title"):
                    out.append({"title": it["title"], "why": it.get("why", ""), "risk": it.get("risk", "")})
            if out:
                return out

        return [{"title": "리틀 포레스트"}, {"title": "캐롤"}]

    def respond(self, **kwargs):
        return self.respond_recommend(
            common_rules=COMMON_OUTPUT_RULES,
            conversation_rules=CONVERSATION_RULES,
            next_turn="",  # ← 빈 문자열
            **kwargs
        )
