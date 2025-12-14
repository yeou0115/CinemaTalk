import os
import requests
from urllib.parse import quote


TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # v3 API Key


def get_poster_url(movie_title: str) -> str | None:
    """
    영화 제목으로 TMDB 검색 → 가장 상단 결과의 포스터 URL 반환
    API 키 없거나 실패 시 None
    """
    if not TMDB_API_KEY or not movie_title:
        return None

    try:
        query = quote(movie_title)
        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}"
            f"&query={query}"
            "&language=ko-KR"
        )

        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()

        results = data.get("results", [])
        if not results:
            return None

        poster_path = results[0].get("poster_path")
        if not poster_path:
            return None

        return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception:
        return None
