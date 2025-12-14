# utils/tmdb.py
import os
import requests

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w300"

def get_poster(title: str):
    if not TMDB_API_KEY:
        return None
    try:
        r = requests.get(
            f"{BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "ko-KR",
            },
            timeout=5,
        )
        data = r.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return IMAGE_BASE + poster_path
    except Exception:
        return None
    return None
