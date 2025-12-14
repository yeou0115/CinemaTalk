import streamlit as st
from typing import Dict, List

from main import run_turn
from utils.tmdb import get_poster_url


# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="🎬 시네마TALK",
    page_icon="🎥",
    layout="centered"
)

st.title("🎬 시네마TALK")
st.caption("영화를 사랑하는 서로 다른 사람들이 모여 수다 떨듯 추천해주는 영화 톡방")


# -------------------------
# session state 초기화
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict] = [] # type: ignore

if "context" not in st.session_state:
    st.session_state.context = {}

if "shown_posters" not in st.session_state:
    st.session_state.shown_posters = set()

if "initialized" not in st.session_state:
    st.session_state.initialized = False


# -------------------------
# 초기 인사 (진행자)
# -------------------------
if not st.session_state.initialized:
    st.session_state.messages.append({
        "role": "assistant",
        "speaker": "🎤 호스트",
        "text": (
            "안녕! 여기는 **시네마TALK** 🎬\n\n"
            "영화 덕후, 영화 전문가, 그리고 대중 관객까지—\n"
            "서로 다른 취향을 가진 사람들이 한 톡방에서 영화 얘기하는 공간이야.\n\n"
            "🎄 연말 영화 추천, 🎥 감독·배우 기반 추천, 📽️ 영화 큐레이션까지\n"
            "편하게 말 걸어줘! 누구한테 물어보고 싶은지도 같이 말해도 좋아 😊"
        )
    })
    st.session_state.initialized = True


# -------------------------
# 메시지 렌더링
# -------------------------
def render_message(msg: Dict):
    role = "assistant" if msg["role"] == "assistant" else "user"

    with st.chat_message(role):
        if msg.get("speaker"):
            st.markdown(f"**{msg['speaker']}**")

        # 🎬 포스터 표시 (assistant + movie_title 있을 때)
        movie_title = msg.get("movie_title")
        if role == "assistant" and movie_title:
            if movie_title not in st.session_state.shown_posters:
                poster_url = get_poster_url(movie_title)
                if poster_url:
                    st.image(poster_url, width=220)
                    st.session_state.shown_posters.add(movie_title)

        st.markdown(msg["text"])


# -------------------------
# 기존 메시지 출력
# -------------------------
for m in st.session_state.messages:
    render_message(m)


# -------------------------
# 사이드바 UI
# -------------------------
with st.sidebar:
    st.subheader("🎭 누구에게 물어볼까?")
    targets = st.multiselect(
        "답변을 받을 큐레이터를 선택하세요",
        ["모두", "영화덕후", "영화전문가", "대중관객"],
        default=["모두"]
    )

    st.divider()

    if st.button("🧹 대화 초기화"):
        st.session_state.messages = []
        st.session_state.context = {}
        st.session_state.shown_posters = set()
        st.session_state.initialized = False
        st.rerun()


# -------------------------
# 사용자 입력
# -------------------------
user_input = st.chat_input("예: 크리스마스에 연인이랑 볼 영화 추천해줘")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "speaker": "🙋 나",
        "text": user_input
    })

    render_message(st.session_state.messages[-1])

    # 로딩 표시
    with st.spinner("🎬 큐레이터들이 열심히 떠드는 중..."):
        responses, updated_context = run_turn(
            user_input=user_input,
            context=st.session_state.context,
            targets=targets
        )

    # 응답 메시지 추가
    for r in responses:
        st.session_state.messages.append(r)
        render_message(r)

    st.session_state.context = updated_context
