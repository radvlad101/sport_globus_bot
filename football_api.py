# football_data_api.py
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

API_BASE_URL = "https://api.football-data.org/v4"
#leagues = ["PL", "PD", "SA", "BL1", "FL1", "CL", "EL"]

def get_fixtures(leagues: List[str], api_key: str, limit_matches: Dict[str, int]) -> Dict[str, Any]:
    """
    Получает данные о матчах (fixtures) по выбранным лигам.

    :param leagues: список кодов лиг (например ["PL", "PD", "SA"] для АПЛ, Ла Лига, Серия А)
    :param api_key: API ключ для football-data.org
    :param limit_matches: словарь {league_code: количество_матчей}, сколько ближайших матчей выводить
    :return: словарь с результатами (JSON)
    """

    headers = {
        "X-Auth-Token": api_key
    }

    results = {}
    today = datetime.now(timezone.utc)             # текущая дата UTC (offset-aware)
    next_week = today + timedelta(days=7)          # дата через неделю

    for league_code in leagues:
        url = f"{API_BASE_URL}/competitions/{league_code}/matches"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            results[league_code] = {"error": response.text}
            continue

        data = response.json()
        matches = data.get("matches", [])

        # фильтр по ближайшей неделе
        upcoming_matches = []
        for match in matches:
            match_date = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            if today <= match_date <= next_week:
                upcoming_matches.append(match)

        # ограничение по количеству матчей для этой лиги
        limit = limit_matches.get(league_code, 5)
        results[league_code] = upcoming_matches[:limit]

    return results
