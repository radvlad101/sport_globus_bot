from football_api import get_fixtures

API_KEY = "8c614bb489684b5db605738b43650d89"

leagues = ["PL", "PD", "SA"]  # АПЛ, Ла Лига, Серия А
limit_matches = {
    "PL": 5,
    "PD": 3,
    "SA": 4
}

fixtures = get_fixtures(leagues, API_KEY, limit_matches)
print(fixtures)

