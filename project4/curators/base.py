import json
from typing import Any, Dict, List, Tuple
from utils.kobis import KobisClient
from utils.llm import ask_llm

def safe_json_loads(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None

class CuratorBot:
    label: str
    system: str

    def __init__(self, label: str, system: str, kobis: KobisClient):
        self.label = label
        self.system = system
        self.kobis = kobis

    def llm(self, user: str, temperature: float = 0.9) -> str:
        return ask_llm(self.system, user, temperature=temperature)

    def think_recommend(self, user_input: str, constraints: Dict) -> List[Dict]:
        raise NotImplementedError

    def verify_movies(self, titles: List[str]) -> Dict[str, Any]:
        return self.kobis.verify_titles(titles)

    def respond_recommend(
        self,
        user_input: str,
        ideas: List[Dict],
        facts: Dict[str, Any],
        constraints: Dict,
        previous_messages: str,
        used_titles: List[str],
        common_rules: str,
        conversation_rules: str,
        next_turn: str,
    ) -> Tuple[str, List[str]]:
        # 항상 정의
        picked = [x.get("title") for x in ideas if x.get("title")][:2]

        prompt = f"""
{common_rules}
{conversation_rules}

[사용자 질문]
{user_input}

[앞서 말한 다른 큐레이터 발화]
{previous_messages}

[이미 언급된 영화 목록]
{used_titles}

[너의 1차 후보(참고)]
{ideas}

[API로 확인한 메타데이터(있으면 근거로 1~2문장만 활용)]
{facts}

{next_turn}
"""
        text = self.llm(prompt, temperature=0.9)
        return text, picked # type: ignore
