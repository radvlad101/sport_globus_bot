#football_api.py
import logging
import requests
from config import API_KEY_the_odds_api
from datetime import date, timedelta,datetime
from typing import List, Dict,Any
from config import API_KEY_latest_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_latest_news(language="ru"):
    """Отримує найпопулярнішу футбольну новину за останні 24 години з NewsAPI.org."""
    now = datetime.utcnow()
    yesterday = now - timedelta(days=3)
    from_date = yesterday.strftime("%Y-%m-%dT%H:%M:%S")
    to_date = now.strftime("%Y-%m-%dT%H:%M:%S")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "football OR soccer",
        "from": from_date,
        "to": to_date,
        "language": language,
        "sortBy": "popularity",
        "pageSize": 5,
        "apiKey": API_KEY_latest_news
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        logger.error(f"Помилка при отриманні даних: {response.status_code}")
        return None

    articles = response.json().get("articles", [])
    if not articles:
        logging.info(f"Немає новин за останні 24 години на {language}")
        return None

    top_article = articles[0]
    return {
        "title": top_article["title"],
        "link": top_article["url"],
        "summary": top_article.get("description", ""),
        "published": top_article["publishedAt"],
        "source": top_article["source"]["name"],
        "image": top_article.get("urlToImage")
    }

def format_date_with_flag(date: str, commence_flag: str) -> str:
    if commence_flag == "commenceTimeFrom":
        return f"{date}T00:00:00Z"
    elif commence_flag == "commenceTimeTo":
        return f"{date}T23:59:00Z"
    else:
        raise ValueError(f"Неподдерживаемый флаг: {commence_flag}. "
                         "Допустимые значения: 'commenceTimeFrom', 'commenceTimeTo'")


def odds_events(sport,commenceTimeFrom,commenceTimeTo):

    base_url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY_the_odds_api,
        "bookmakers": "onexbet",
        "oddsFormat": "decimal",  # пробелы автоматически закодируются
        "commenceTimeFrom":commenceTimeFrom,
        "commenceTimeTo":commenceTimeTo
    }
    # Делаем запрос
    api_call = requests.get(base_url, params=params)
    response = api_call.json()
    return  response
    #print(f"{response}")
#empty_badge =0

def get_badge(team):
    #global empty_badge
    badge = ''

    base_url = f"https://www.thesportsdb.com/api/v1/json/123/searchteams.php?"
    params = {
        "t": team  # пробелы автоматически закодируются
    }
    resp = requests.get(base_url, params=params).json()
    if resp==None or resp['teams']==None:
        #empty_badge+=1
        return badge
    badge = resp.get("teams", [{}])[0].get("strBadge")
    return badge
    #print(badge)  # https://r2.thesportsdb.com/images/media/team/badge/xxx.png


def clean_team_name(team_name: str) -> str:
    """Удаляет различные числовые префиксы"""
    import re
    patterns = [
        r'^\d+\.\s*',  # "1. "
        r'^\d+\s*',  # "1 "
        r'^#\d+\s*',  # "#1 "
        r'^\(\d+\)\s*',  # "(1) "
    ]

    for pattern in patterns:
        team_name = re.sub(pattern, '', team_name)

    return team_name.strip()

#odds_events()
# sport = 'soccer_germany_bundesliga'
def get_events_by_sport_and_date(sport: str, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = date_to.strftime("%Y-%m-%d")
    commenceTimeFrom = format_date_with_flag(date_from_str,"commenceTimeFrom")
    commenceTimeTo = format_date_with_flag(date_to_str,"commenceTimeTo")
    events = odds_events (sport,commenceTimeFrom,commenceTimeTo)

    print(f"{events}")
    for event in events:
        home_team = clean_team_name (event.get('home_team', ''))
        print(f"{home_team}")
        away_team = clean_team_name(event.get('away_team', ''))
        print(f"{away_team}")
        if home_team !='':
            badge = get_badge(home_team)
            event['home_team_badge'] = badge
        if away_team !='':
            badge = get_badge(away_team)
            event['away_team_badge'] = badge

    return events
"""
date_event = date.today() + timedelta(days=3)
events = get_events_by_sport_and_date('soccer_germany_bundesliga',date_event,date_event)
print(f"{events}")
print("empty_badge"+ str(empty_badge))
"""





# resp=get_events(sport,commenceTimeFrom,commenceTimeTo)
# team = resp[0]

# get_badge(team["strBadge"])
