import requests
import logging
from typing import List, Dict, Any

API_URL = "https://api.football-data.org/v4/competitions/{league}/matches"

def get_fixtures(leagues: List[str], api_key: str, limit_matches: Dict[str, int]) -> Dict[str, Any]:
    """
    Получаем ближайшие матчи по выбранным лигам.
    Возвращает dict:
    {
      "APL": [ { "homeTeam": {...}, "awayTeam": {...}, "odds": {...} }, ... ],
      "LaLiga": [...],
      ...
    }
    """
    headers = {"X-Auth-Token": api_key}
    all_fixtures: Dict[str, Any] = {}

    for league in leagues:
        try:
            url = API_URL.format(league=league)
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            data = resp.json()
            matches = data.get("matches", [])
            logging.debug(f"[DEBUG] Лига {league} вернула {len(matches)} матчей")

            if matches:
                logging.debug(f"[DEBUG] Пример матча {league}: {matches[0]}")

            # ограничиваем кол-во матчей
            max_matches = limit_matches.get(league, len(matches))
            filtered = []

            for match in matches[:max_matches]:
                fixture = {
                    "homeTeam": match.get("homeTeam", {}),
                    "awayTeam": match.get("awayTeam", {}),
                    "utcDate": match.get("utcDate"),
                    "status": match.get("status"),
                    "odds": match.get("odds", {})  # ⚽ если API отдает коэффициенты
                }
                filtered.append(fixture)

            all_fixtures[league] = filtered

        except Exception as e:
            logging.error(f"[ERROR] Не удалось получить матчи для {league}: {e}")
            all_fixtures[league] = []

    return all_fixtures
