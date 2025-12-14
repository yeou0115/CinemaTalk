from typing import Dict, List, Tuple

from curators.cinephile import CinephileBot
from curators.critic import CriticBot
from curators.popular import PopularBot
from utils.kobis import KobisClient


def run_turn(
    user_input: str,
    context: Dict,
    targets: List[str],
) -> Tuple[List[Dict], Dict]:
    """
    - 큐레이터들은 서로 언급하지 않음
    - 추천 영화는 절대 겹치지 않도록 main에서 강제
    """

    # --------------------
    # context 초기화
    # --------------------
    if "used_titles" not in context:
        context["used_titles"] = []
    if "history" not in context:
        context["history"] = []

    kobis = KobisClient()

    # --------------------
    # curator 인스턴스
    # --------------------
    cinephile = CinephileBot(kobis)
    critic = CriticBot(kobis)
    popular = PopularBot(kobis)

    curator_map = {
        "영화덕후": cinephile,
        "영화전문가": critic,
        "대중관객": popular,
    }

    # --------------------
    # 대상 선택
    # --------------------
    if "모두" in targets:
        selected = list(curator_map.values())
    else:
        selected = [curator_map[t] for t in targets if t in curator_map]

    responses: List[Dict] = []

    # --------------------
    # 큐레이터 발화
    # --------------------
    for bot in selected:
        # ✅ 이미 추천된 영화는 절대 고르지 말라는 제약
        constraints = {
            "forbidden_titles": context["used_titles"].copy()
        }

        ideas = bot.think_recommend(
            user_input=user_input,
            constraints=constraints
        )

        # 후보 제목
        titles = [x["title"] for x in ideas if x.get("title")]

        # 혹시라도 겹친 경우를 대비한 2차 방어
        titles = [
            t for t in titles
            if t not in context["used_titles"]
        ]

        facts = bot.verify_movies(titles)

        text, picked = bot.respond(
            user_input=user_input,
            ideas=ideas,
            facts=facts,
            constraints=constraints,
            previous_messages="",   # ❗ 서로 발화 언급 안 함
            used_titles=context["used_titles"],
        )

        # 최종 선택 영화 기록
        context["used_titles"].extend(picked)
        context["history"].append((bot.label, text))

        responses.append({
            "role": "assistant",
            "speaker": bot.label,
            "text": text,
            "movie_title": picked[0] if picked else None,
        })

    # --------------------
    # 진행자 멘트
    # --------------------
    responses.append({
        "role": "assistant",
        "speaker": "🎤 진행자",
        "text": (
            "어때? 추천 받은 영화가 마음에 들어?"
            "마음에 드는 영화가 있으면 그 영화에 대해 더 자세히 설명해줄 수 있어!"
            "아니면 다른 영화 추천을 요청해도 좋아."
        )
    })

    return responses, context
