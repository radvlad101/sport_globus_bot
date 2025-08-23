import os
import logging
import feedparser
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import requests
from datetime import datetime, timedelta
# Новий імпорт для асинхронного перекладача
#from googletrans import AsyncTranslator
from deep_translator import GoogleTranslator
from football_api import get_fixtures
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# Імпорти для Telegram-бота
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Константи та налаштування
# Використовуйте змінні середовища для безпеки в продакшені
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
# AI21_API_KEY = os.getenv("AI21_API_KEY")
# WEBHOOK_URL = os.getenv("WEBHOOK_URL")

TELEGRAM_TOKEN = "8495882876:AAH1xwbeyOqPRkquvz7aijF5iHa6US3IgNg"
TELEGRAM_CHANNEL_ID = "@sport_globus"
AI21_API_KEY = "f46255e8-8dfb-4bdb-abf0-cc8eb4450cd0"
WEBHOOK_URL = "https://sport-globus-bot.onrender.com/webhook"  # Замініть на ваш URL від Render.com

FOOTBALL_API_KEY = "1a351adf0f2692224a02a9741f5039e7"     # https://dashboard.api-football.com/profile?access

API_KEY = "bd6718b87c854edc8baf0880ac7e6992"

logging.basicConfig(level=logging.INFO)

# Ініціалізація клієнтів
ai21_client = AI21Client(api_key=AI21_API_KEY)
#translator = AsyncTranslator()


from football_api import get_fixtures
from football_posting import post_fixtures_with_odds
import asyncio





# Функція отримання новин
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
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        logging.error(f"Помилка при отриманні даних: {response.status_code}")
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


# Функція публікації новин
# Функція публікації новин
async def post_news(app):
    from telegram import InputMediaPhoto

    # --- Русская новость ---
    logging.info("Attempting to get Russian news...")
    news_ru = get_latest_news(language="ru")
    if news_ru:
        logging.info("Russian news found. Attempting to post...")
        caption = f"📰 {news_ru['title']}\n\n{news_ru['summary']}\n\n🔗 Подробнее: {news_ru['link']}"
        try:
            if news_ru.get("image"):
                await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_ru["image"], caption=caption)
            else:
                await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption)
            logging.info("Russian news posted successfully.")
        except Exception as e:
            logging.error(f"Error posting Russian news: {e}")
    else:
        logging.warning("No Russian news found.")

    # --- Английская новость с переводом ---
    logging.info("Attempting to get English news...")
    news_en = get_latest_news(language="en")
    if news_en:
        logging.info("English news found. Attempting to translate and post...")
        try:
            translator = GoogleTranslator(source='en', target='ru')
            title_ru = translator.translate(news_en["title"])
            summary_ru = translator.translate(news_en.get("summary", ""))
            logging.info("Translation successful.")

            caption = f"📰 {title_ru}\n\n{summary_ru}\n\n🔗 Подробнее: {news_en['link']}"

            if news_en.get("image"):
                await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_en["image"], caption=caption)
            else:
                await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption)
            logging.info("English news posted successfully.")
        except Exception as e:
            logging.error(f"Error posting English news with translation: {e}")
    else:
        logging.warning("No English news found.")




# Функція сумаризації
def summarize_text(text: str) -> str:
    """Використовує AI21 для сумаризації тексту."""
    try:
        response = ai21_client.chat.completions.create(
            model="jamba-large-1.7",
            messages=[ChatMessage(role="user", content=f"Сделай краткое резюме этой новости:\n\n{text}")]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"AI21 помилка: {e}")
        return None

async def post_fixtures_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публікує новину в канал за командою."""

    API_KEY = "8c614bb489684b5db605738b43650d89"
    leagues = ["PL", "PD", "SA", "BL1", "FL1"]
    limit_matches = {"PL": 5, "PD": 3, "SA": 4, "BL1": 3, "FL1": 3}

    fixtures_data = get_fixtures(leagues, API_KEY, limit_matches)
    # Внутри вашего async приложения
    await post_fixtures_with_odds(context.application, fixtures_data)
    await update.message.reply_text("📰 МАТЧИ опубліковано вручну!")




# Команда /post_now
async def post_news_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публікує новину в канал за командою."""
    await post_news(context.application)
    await update.message.reply_text("📰 Новину опубліковано вручну!")


# Головна функція запуску
def main():
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("post_news_now", post_news_now))
        app.add_handler(CommandHandler("post_fixtures_now", post_fixtures_now))

        # Використання web-сервера для webhook
        port = int(os.environ.get("PORT", 5000))

        # Встановлення webhook
        # app.run_webhook сам встановить webhook URL на Render.com
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=WEBHOOK_URL
        )

        logging.info("✅ Бот успішно запущено!")

    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()
    # Цей код виконується лише при локальному запуску і не блокує веб-сервер
    # news = get_latest_news()
    # if news:
    #     print("📰", news["title"])
    #     print("🔗", news["link"])
    #     print("📝", news["summary"])
    #     print("🖼", news["image"])