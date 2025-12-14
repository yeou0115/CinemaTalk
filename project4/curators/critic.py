from typing import Dict, List
from curators.base import CuratorBot, safe_json_loads
from curators.prompts import (
    CRITIC_SYSTEM, COMMON_OUTPUT_RULES, CONVERSATION_RULES, NEXT_TURN_SUGGESTIONS
)
from utils.kobis import KobisClient

class CriticBot(CuratorBot):
    def __init__(self, kobis: KobisClient):
        super().__init__("🎓 영화전문가", CRITIC_SYSTEM, kobis)

    def think_recommend(self, user_input: str, constraints: Dict) -> List[Dict]:
        prompt = f"""
사용자 요청: {user_input}

전문가 관점에서 추천 영화 1~2편만 고르라.
반드시 JSON 배열로만 출력:
[
  {{"title":"영화제목", "thesis":"왜 이 질문에 적합한지(짧게)"}},
  ...
]
"""
        raw = self.llm(prompt, temperature=0.8)
        data = safe_json_loads(raw)
        if isinstance(data, list) and data:
            out = []
            for it in data[:2]:
                if isinstance(it, dict) and it.get("title"):
                    out.append({"title": it["title"], "thesis": it.get("thesis", "")})
            if out:
                return out
        return [{"title": "기생충"}]

    def respond(self, **kwargs):
        return self.respond_recommend(
            common_rules=COMMON_OUTPUT_RULES,
            conversation_rules=CONVERSATION_RULES,
            next_turn="",  # ← 빈 문자열
            **kwargs
        )
