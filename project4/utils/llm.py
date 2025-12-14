import os
from dotenv import load_dotenv
from openai import OpenAI

# ✅ .env 로드
load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

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
