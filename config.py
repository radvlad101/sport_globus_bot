#config.py
# TELEGRAM DATA

# TELEGRAM BOT  @sport_globus_bot
TELEGRAM_TOKEN = "8495882876:AAH1xwbeyOqPRkquvz7aijF5iHa6US3IgNg"

# TELEGRAM CHANNEL @sport_globus
TELEGRAM_CHANNEL_ID = "@sport_globus"

# Хост Render.com  URL+ /webhook   для TELEGRAM BOT
WEBHOOK_URL = "https://sport-globus-bot.onrender.com/webhook"

# https://newsapi.org/  это популярный API для доступа к новостям из тысяч источников  по всему миру
API_KEY_latest_news = "bd6718b87c854edc8baf0880ac7e6992"

# https://www.ai21.com/
# Сервис AI21 Labs предлагает API для суммаризации текста через свои языковые модели
AI21_API_KEY = "f46255e8-8dfb-4bdb-abf0-cc8eb4450cd0"



# https://www.thesportsdb.com
"""
An open, crowd-sourced sports database of artwork and metadata with a free sports API.
The sports database is only possible, thanks to the hard work of our users.
If you like the site, please consider registering as an editor or click below...
"""
API_URL_thesportsdb = "https://www.thesportsdb.com/api/v1/json/{api_key}/eventsday.php?d={date}&s=Soccer&l={league}"
API_KEY_thesportsdb ='123' #free plan

# https://www.thesportsdb.com
"""
'idLeague'
'English Premier League' =  '4328'
'English League Championship''4329'
'German Bundesliga''4331'
'Italian Serie A''4332'
'French Ligue 1''4334'
'Spanish La Liga''4335'
'Russian Football Premier League''4355'
'Turkish Super Lig''4339'
'Mexican Primera League''4350'
'Brazilian Serie A''4351'
'Ukrainian Premier League''4354'
"""


leagues = ['English Premier League','Spanish La Liga','German Bundesliga','Italian Serie A','Russian Football Premier League','Ukrainian Premier League']
#leagues = ['English Premier League']

#Бесплатные или условно-бесплатные источники odds https://the-odds-api.com

league_odds_api_to_thesportsdb = {
    'soccer_epl':'English Premier League','soccer_spain_la_liga':'Spanish La Liga',
    'soccer_germany_bundesliga':'German Bundesliga','soccer_italy_serie_a':'Italian Serie A'
}
team_odds_api_to_thesportsdb= {'home_team': 'strHomeTeam', 'away_team': 'strAwayTeam'}

"""
"key":
'soccer_epl' 'soccer_spain_la_liga'  'soccer_germany_bundesliga' 'soccer_italy_serie_a'    '' '' '' '' '' '' '' '' '' '' '' 
"""

#ODDS  https://the-odds-api.com/account/?redirect=false  FREE   500 credits per month  $0 per month https://dash.the-odds-api.com/api-subscriptions
API_KEY_the_odds_api ='4a1b24e3e234587ae0c377581e6e3854'

#https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d=2025-08-29&s=Soccer&l=German Bundes
strLeagueBadges =[
    {
        'idLeague': '4328',
        'strLeague': 'English Premier League',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/gasy9d1737743125.png'
    },
    {
        'idLeague': '4328',
        'strLeague': 'English League Championship',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/ty5a681688770169.png'
    },
    {
        'idLeague': '4331',
        'strLeague': 'German Bundesliga',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/teqh1b1679952008.png'
    },
    {
        'idLeague': '4332',
        'strLeague': 'Italian Serie A',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/67q3q21679951383.png'

    },
    {
        'idLeague': '4335',
        'strLeague': 'Spanish La Liga',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/ja4it51687628717.png'
    },
    {
        'idLeague': '4355',
        'strLeague': 'Russian Football Premier League',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/d4yp7g1690178551.png'

    },
    {
        'idLeague': '4354',
        'strLeague': 'Ukrainian Premier League',
        'strLeagueBadge': 'https://r2.thesportsdb.com/images/media/league/badge/qprvpy1471773025.png'
    }

]



#TELEGRAM_TOKEN = "8495882876:AAH1xwbeyOqPRkquvz7aijF5iHa6US3IgNg"
#TELEGRAM_CHANNEL_ID = "@sport_globus"
#AI21_API_KEY = "f46255e8-8dfb-4bdb-abf0-cc8eb4450cd0"
#WEBHOOK_URL = "https://sport-globus-bot.onrender.com/webhook"  # Замініть на ваш URL від Render.com

#FOOTBALL_API_KEY = "1a351adf0f2692224a02a9741f5039e7"     # https://dashboard.api-football.com/profile?access

#API_KEY_latest_news = "bd6718b87c854edc8baf0880ac7e6992" #https://newsapi.org/  это популярный API для доступа к новостям из тысяч источников по всему миру

