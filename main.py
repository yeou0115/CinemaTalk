import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from utils.kobis import KobisClient
from curators.cinephile import CinephileBot
from curators.critic import CriticBot
from curators.popular import PopularBot


# -----------------------------
# Intent 분류 (간단·안정)
# -----------------------------
def classify_intent(text: str) -> Dict:
    t = text.strip()

    if "감독" in t:
        m = re.search(r"(.+?)\s*감독", t)
        return {"type": "recommend", "criteria": "director", "value": m.group(1).strip() if m else ""}

    if "배우" in t or "출연" in t:
        m = re.search(r"(.+?)\s*(배우|출연)", t)
        return {"type": "recommend", "criteria": "actor", "value": m.group(1).strip() if m else ""}

    if any(k in t for k in ["박스오피스", "흥행", "유명", "명작", "시대", "년대"]):
        return {"type": "recommend", "criteria": "boxoffice", "value": None}

    return {"type": "curation", "criteria": None, "value": None}


# -----------------------------
# API 기반 후보 생성
# -----------------------------
def build_api_candidates(kobis: KobisClient, intent: Dict, used_titles: List[str]) -> List[str]:
    titles = []

    # -----------------------------
    # 감독 기반
    # -----------------------------
    if intent["criteria"] == "director" and intent["value"]:
        data = kobis.search_movie_list(
            directorNm=intent["value"],
            itemPerPage=30
        )
        for m in data:
            name = m.get("movieNm") # type: ignore
            if name and name not in used_titles:
                titles.append(name)

    # -----------------------------
    # 배우 기반
    # -----------------------------
    elif intent["criteria"] == "actor" and intent["value"]:
        people = kobis.search_people_list(
            peopleNm=intent["value"],
            itemPerPage=5
        )
        if people:
            people_cd = people[0].get("peopleCd") # type: ignore
            if people_cd:
                info = kobis.search_people_info(people_cd)
                filmos = info.get("filmos", [])
                for f in filmos:
                    name = f.get("movieNm")
                    if name and name not in used_titles:
                        titles.append(name)

    # -----------------------------
    # 박스오피스 기반
    # -----------------------------
    elif intent["criteria"] == "boxoffice":
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        data = kobis.search_weekly_boxoffice_list( # type: ignore
            targetDt=date,
            weekGb="0",
            itemPerPage=10
        )
        for m in data:
            name = m.get("movieNm")
            if name and name not in used_titles:
                titles.append(name)

    # 중복 제거 + 순서 유지
    out = []
    for t in titles:
        if t not in out:
            out.append(t)

    return out



# -----------------------------
# 메인 엔트리
# -----------------------------
def run_turn(user_input: str, context: Dict, targets: List[str]) -> Tuple[List[Dict], Dict]:
    context.setdefault("used_titles", [])

    kobis = KobisClient()

    bots = {
        "영화덕후": CinephileBot(kobis),
        "영화전문가": CriticBot(kobis),
        "대중관객": PopularBot(kobis),
    }

    selected_bots = (
        bots.values()
        if "모두" in targets
        else [bots[t] for t in targets if t in bots]
    )

    intent = classify_intent(user_input)
    responses = []

    # -----------------------------
    # 추천: API가 후보 생성
    # -----------------------------
    if intent["type"] == "recommend":
        candidates = build_api_candidates(kobis, intent, context["used_titles"])

        for bot in selected_bots:
            if not candidates:
                break

            title = candidates.pop(0)
            ideas = [{"title": title}]
            facts = bot.verify_movies([title])

            text, picked = bot.respond(
                user_input=user_input,
                ideas=ideas,
                facts=facts,
                constraints={"forbidden_titles": context["used_titles"]},
                previous_messages="",
                used_titles=context["used_titles"],
            )

            context["used_titles"].extend(picked)

            responses.append({
                "role": "assistant",
                "speaker": bot.label,
                "text": text,
                "movie_title": picked[0] if picked else title,
            })

    # -----------------------------
    # 큐레이션: LLM이 후보 생성
    # -----------------------------
    else:
        for bot in selected_bots:
            ideas = bot.think_recommend(
                user_input=user_input,
                constraints={"forbidden_titles": context["used_titles"]}
            )

            ideas = [
                i for i in ideas
                if i.get("title") and i["title"] not in context["used_titles"]
            ]

            if not ideas:
                continue

            title = ideas[0]["title"]
            facts = bot.verify_movies([title])

            text, picked = bot.respond(
                user_input=user_input,
                ideas=[{"title": title}],
                facts=facts,
                constraints={"forbidden_titles": context["used_titles"]},
                previous_messages="",
                used_titles=context["used_titles"],
            )

            context["used_titles"].extend(picked)

            responses.append({
                "role": "assistant",
                "speaker": bot.label,
                "text": text,
                "movie_title": picked[0] if picked else title,
            })

    # -----------------------------
    # 진행자 발화 (항상 마지막)
    # -----------------------------
    responses.append({
        "role": "assistant",
        "speaker": "🎤 진행자",
        "text": (
            "지금 추천 중에서 끌리는 영화 있어?\n"
            "아니면 기준을 바꿔볼까?\n"
            "예) 배우로 다시 추천 / 분위기 더 가볍게 / 연말 감성으로"
        )
    })

    return responses, context
