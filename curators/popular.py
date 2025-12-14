from datetime import datetime, timedelta
from typing import Dict, List

from curators.base import CuratorBot, safe_json_loads
from curators.prompts import (
    POPULAR_SYSTEM, COMMON_OUTPUT_RULES, CONVERSATION_RULES, NEXT_TURN_SUGGESTIONS
)
from utils.kobis import KobisClient

class PopularBot(CuratorBot):
    def __init__(self, kobis: KobisClient):
        super().__init__("🍿 대중관객", POPULAR_SYSTEM, kobis)

    def think_recommend(self, user_input: str, constraints: Dict) -> List[Dict]:
        # 1) 박스오피스에서 씨드 뽑기 (전일)
        seed_titles: List[str] = []
        try:
            target = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            data = self.kobis.daily_boxoffice(targetDt=target, itemPerPage=10)
            items = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", []) or []
            seed_titles = [x.get("movieNm") for x in items if x.get("movieNm")]
        except Exception:
            seed_titles = []

        # 2) LLM에 1~2편 최종 선택을 맡김
        prompt = f"""
사용자 요청: {user_input}
가능하면 아래 트렌드 후보를 참고해서, 오늘 당장 보기 좋은 영화 1~2편을 골라라.
트렌드 후보: {seed_titles[:8]}

반드시 JSON 배열로만 출력:
[
  {{"title":"영화제목", "why":"이유(짧게)"}},
  ...
]
"""
        raw = self.llm(prompt, temperature=0.7)
        data = safe_json_loads(raw)
        if isinstance(data, list) and data:
            out = []
            for it in data[:2]:
                if isinstance(it, dict) and it.get("title"):
                    out.append({"title": it["title"], "why": it.get("why", "")})
            if out:
                return out

        # fallback
        return [{"title": seed_titles[0]}] if seed_titles else [{"title": "나 홀로 집에"}]

    def respond(self, **kwargs):
        return self.respond_recommend(
            common_rules=COMMON_OUTPUT_RULES,
            conversation_rules=CONVERSATION_RULES,
            next_turn="",  # ← 빈 문자열
            **kwargs
        )

