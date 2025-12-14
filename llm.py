import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ✅ .env 로드 (로컬 실행용)
load_dotenv()

# [수정된 로직] 일단 로컬 환경변수에서 가져오고, secrets가 있으면 거기서 덮어쓰기
api_key = os.getenv("OPENAI_API_KEY")
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

try:
    # 클라우드(Streamlit Cloud) 환경인지 확인
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    if "OPENAI_MODEL" in st.secrets:
        _MODEL = st.secrets["OPENAI_MODEL"]
except:
    # 로컬에 secrets.toml 파일이 없으면 그냥 넘어감 (로컬 키 사용)
    pass

# 클라이언트 생성
_client = OpenAI(api_key=api_key)

def ask_llm(system: str, user: str, temperature: float = 0.9) -> str:
    res = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return (res.choices[0].message.content or "").strip()