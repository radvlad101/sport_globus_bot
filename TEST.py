# TEST.py
from football_api import get_fixtures

API_KEY = "8c614bb489684b5db605738b43650d89"

# ID лиг в API-Football
# 39 - АПЛ, 140 - Ла Лига, 135 - Серия А
leagues = [39, 140, 135]

# Сколько матчей брать по каждой лиге
limit_matches = {
    39: 5,   # АПЛ – 5 матчей
    140: 3,  # Ла Лига – 3 матча
    135: 7   # Серия А – 7 матчей
}

fixtures = get_fixtures(leagues, "fixtures", API_KEY, limit_matches)

print(fixtures)
