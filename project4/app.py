import streamlit as st
from main import run_turn
from utils.tmdb import get_poster

# --------------------
# 페이지 설정
# --------------------
st.set_page_config(
    page_title="🎬 영화 큐레이터 톡방",
    page_icon="🎬",
    layout="wide"
)

# --------------------
# 제목 & 설명
# --------------------
st.title("🎬 영화 큐레이터 톡방")
st.caption(
    "영화덕후, 영화전문가, 대중관객이 한 톡방에서 "
    "각자 스타일로 영화 추천과 큐레이션을 해줘요."
)

# --------------------
# session state
# --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = {}

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "shown_posters" not in st.session_state:
    st.session_state.shown_posters = set()

# --------------------
# 사이드바
# --------------------
with st.sidebar:
    st.subheader("🎛 대화 설정")

    targets = st.multiselect(
        "누구에게 물어볼까요?",
        ["모두", "영화덕후", "영화전문가", "대중관객"],
        default=["모두"]
    )

    if st.button("🧹 대화 전체 초기화"):
        st.session_state.messages = []
        st.session_state.context = {}
        st.session_state.initialized = False
        st.session_state.shown_posters = set()
        st.rerun()

    st.caption("🎞 포스터 이미지 제공: TMDB")

# --------------------
# 진행자 첫 인사
# --------------------
if not st.session_state.initialized:
    st.session_state.messages.append({
        "role": "assistant",
        "speaker": "🎤 진행자",
        "text": (
            "안녕! 여긴 영화 좋아하는 사람들이 모인 톡방이야 😊\n\n"
            "기분이나 상황만 말해줘도 되고,\n"
            "특정 사람한테만 물어봐도 돼.\n\n"
            "오늘 어떤 영화가 땡겨?"
        )
    })
    st.session_state.initialized = True

# --------------------
# 메시지 렌더링
# --------------------
def render_message(msg):
    speaker = msg.get("speaker", "")
    role = "user" if msg.get("role") == "user" else "assistant"

    avatar = {
        "🎤 진행자": "🎤",
        "🎬 영화덕후": "🎬",
        "🎓 영화전문가": "🎓",
        "🍿 대중관객": "🍿",
        "user": None,
    }.get(speaker)

    with st.chat_message(role, avatar=avatar):
        # 발화자 이름 표시
        if role == "assistant" and speaker:
            st.markdown(f"**{speaker}**")

        movie_title = msg.get("movie_title")
        if movie_title and movie_title not in st.session_state.shown_posters:
            poster = get_poster(movie_title)
            if poster:
                st.image(poster, width=200)
                st.session_state.shown_posters.add(movie_title)

        st.markdown(msg["text"])


for m in st.session_state.messages:
    render_message(m)

# --------------------
# 입력창
# --------------------
user_input = st.chat_input(
    "예: 크리스마스에 보기 좋은 영화 추천해줘 🎄"
)

if user_input:
    user_msg = {
        "role": "user",
        "speaker": "user",
        "text": user_input
    }
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    with st.spinner("🎬 큐레이터들이 영화 고르는 중이에요..."):
        responses, new_context = run_turn(
            user_input=user_input,
            context=st.session_state.context,
            targets=targets
        )

    st.session_state.context = new_context

    for r in responses:
        st.session_state.messages.append(r)
        render_message(r)
