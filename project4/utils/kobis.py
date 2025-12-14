import os
import requests
import streamlit as st
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE = "https://www.kobis.or.kr/kobisopenapi/webservice/rest"

class KobisClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        # 1. 우선순위: 직접 입력받은 키
        self.api_key = api_key
        
        # 2. 직접 입력이 없으면 환경변수(.env)에서 먼저 찾음
        if not self.api_key:
            self.api_key = os.getenv("KOBIS_API_KEY", "")

        # 3. 클라우드(Secrets)에 키가 있다면 덮어씌움 (에러 방지 처리)
        try:
            if "KOBIS_API_KEY" in st.secrets:
                self.api_key = st.secrets["KOBIS_API_KEY"]
        except:
            pass
            
        self.timeout = timeout

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            return {"_error": "KOBIS_API_KEY is missing"}
        url = f"{BASE}/{path}"
        params = {"key": self.api_key, **params}
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # --- Boxoffice ---
    def daily_boxoffice(self, targetDt: str, itemPerPage: int = 10, **kwargs) -> Dict[str, Any]:
        return self._get("boxoffice/searchDailyBoxOfficeList.json", {"targetDt": targetDt, "itemPerPage": itemPerPage, **kwargs})

    def weekly_boxoffice(self, targetDt: str, weekGb: str = "0", itemPerPage: int = 10, **kwargs) -> Dict[str, Any]:
        return self._get("boxoffice/searchWeeklyBoxOfficeList.json", {"targetDt": targetDt, "weekGb": weekGb, "itemPerPage": itemPerPage, **kwargs})

    # --- Movie ---
    def search_movie_list(self, movieNm: str = "", directorNm: str = "", curPage: int = 1, itemPerPage: int = 10, **kwargs) -> Dict[str, Any]:
        return self._get("movie/searchMovieList.json", {"movieNm": movieNm, "directorNm": directorNm, "curPage": curPage, "itemPerPage": itemPerPage, **kwargs})

    def search_movie_info(self, movieCd: str) -> Dict[str, Any]:
        return self._get("movie/searchMovieInfo.json", {"movieCd": movieCd})

    # --- People ---
    def search_people_list(self, peopleNm: str, curPage: int = 1, itemPerPage: int = 10, **kwargs) -> Dict[str, Any]:
        return self._get("people/searchPeopleList.json", {"peopleNm": peopleNm, "curPage": curPage, "itemPerPage": itemPerPage, **kwargs})

    def search_people_info(self, peopleCd: str) -> Dict[str, Any]:
        return self._get("people/searchPeopleInfo.json", {"peopleCd": peopleCd})

    # --- Convenience ---
    def verify_titles(self, titles: List[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for t in titles:
            t = (t or "").strip()
            if not t:
                continue
            try:
                data = self.search_movie_list(movieNm=t, itemPerPage=5)
                movies = data.get("movieListResult", {}).get("movieList", []) or []
                if not movies:
                    out[t] = {"found": False}
                    continue
                m = movies[0]
                out[t] = {
                    "found": True,
                    "movieCd": m.get("movieCd"),
                    "movieNm": m.get("movieNm"),
                    "openDt": m.get("openDt"),
                    "genreAlt": m.get("genreAlt"),
                    "nationAlt": m.get("nationAlt"),
                    "directors": [d.get("peopleNm") for d in (m.get("directors") or []) if d.get("peopleNm")],
                }
            except Exception as e:
                out[t] = {"found": False, "error": str(e)}
        return out