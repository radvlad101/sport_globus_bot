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

API_KEY = "bd6718b87c854edc8baf0880ac7e6992"

logging.basicConfig(level=logging.INFO)

# Ініціалізація клієнтів
ai21_client = AI21Client(api_key=AI21_API_KEY)
#translator = AsyncTranslator()


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
    """Публікує новини в Telegram-канал."""
    from telegram import InputMediaPhoto

    # --- Російська новина ---
    news_ru = get_latest_news(language="ru")
    if news_ru:
        caption = f"📰 {news_ru['title']}\n\n{news_ru['summary']}\n\n🔗 Детальніше: {news_ru['link']}"
        try:
            if news_ru.get("image"):
                await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_ru["image"], caption=caption)
            else:
                await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption)
        except Exception as e:
            logging.error(f"Помилка відправлення російської новини: {e}")

    # --- Англійська новина з перекладом (виправлено на deep_translator) ---
    news_en = get_latest_news(language="en")
    if news_en:
        try:
            # Используем синхронный вызов, поэтому 'await' не нужен
            translator = GoogleTranslator(source='en', target='ru')
            title_ru = translator.translate(news_en["title"])
            summary_ru = translator.translate(news_en.get("summary", ""))

            caption = f"📰 {title_ru}\n\n{summary_ru}\n\n🔗 Детальніше: {news_en['link']}"

            if news_en.get("image"):
                await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_en["image"], caption=caption)
            else:
                await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption)
        except Exception as e:
            logging.error(f"Помилка відправлення англійської новини з перекладом: {e}")

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


# Команда /post_now
async def post_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Публікує новину в канал за командою."""
    await post_news(context.application)
    await update.message.reply_text("📰 Новину опубліковано вручну!")


# Головна функція запуску
def main():
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("post_now", post_now))

        # Використання web-сервера для webhook
        port = int(os.environ.get("PORT", 5000))

        # Встановлення webhook
        # app.run_webhook сам встановить webhook URL на Render.com
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/",
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