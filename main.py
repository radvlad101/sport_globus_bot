import os
import logging
import feedparser
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


"""
# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
AI21_API_KEY = os.getenv("AI21_API_KEY")
WEBHOOK_URL = "https://sport-globus-bot.onrender.com/webhook"   #os.getenv("WEBHOOK_URL")
"""

TELEGRAM_TOKEN = "8495882876:AAH1xwbeyOqPRkquvz7aijF5iHa6US3IgNg"
TELEGRAM_CHANNEL_ID = "@sport_globus"
AI21_API_KEY = "f46255e8-8dfb-4bdb-abf0-cc8eb4450cd0"
WEBHOOK_URL = "https://sport-globus-bot.onrender.com/webhook"



logging.basicConfig(level=logging.INFO)

# --- AI21 ---
ai21_client = AI21Client(api_key=AI21_API_KEY)





import requests
from datetime import datetime, timedelta
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

API_KEY = "bd6718b87c854edc8baf0880ac7e6992"

translator = Translator()


def get_latest_news(language="ru"):
    """
    Получает самую популярную футбольную новость за последние 24 часа с NewsAPI.org.
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(days=2)
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
        print("Ошибка при получении данных:", response.status_code)
        return None

    articles = response.json().get("articles", [])
    if not articles:
        print(f"Нет новостей за последние 24 часа на {language}")
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


from googletrans import Translator

translator = Translator()

async def post_news(app: Application):
    news_en = get_latest_news()  # твоя функция, возвращает dict с keys: title, description, urlToImage, url

    if not news_en:
        return

    # Синхронный перевод
    title_ru = translator.translate(news_en["title"], src="en", dest="ru").text
    description_ru = translator.translate(news_en.get("description", ""), src="en", dest="ru").text

    # Английский пост
    caption_en = f"📰 {news_en['title']}\n\n{news_en.get('description', '')}\n\n🔗 Подробнее: {news_en['url']}"
    if news_en.get("urlToImage"):
        try:
            await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_en["urlToImage"], caption=caption_en)
        except Exception as e:
            logging.error(f"Ошибка публикации английского поста: {e}")
    else:
        try:
            await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption_en)
        except Exception as e:
            logging.error(f"Ошибка публикации английского поста: {e}")

    # Русский пост
    caption_ru = f"📰 {title_ru}\n\n{description_ru}\n\n🔗 Подробнее: {news_en['url']}"
    if news_en.get("urlToImage"):
        try:
            await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=news_en["urlToImage"], caption=caption_ru)
        except Exception as e:
            logging.error(f"Ошибка публикации русского поста: {e}")
    else:
        try:
            await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption_ru)
        except Exception as e:
            logging.error(f"Ошибка публикации русского поста: {e}")

    logging.info("✅ Новости опубликованы (EN + RU)")




# --- AI21 суммаризация ---
def summarize_text(text: str) -> str:
    try:
        response = ai21_client.chat.completions.create(
            model="jamba-large-1.7",
            messages=[ChatMessage(role="user", content=f"Сделай краткое резюме этой новости:\n\n{text}")]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"AI21 ошибка: {e}")
        return None



# --- Команда /post_now ---
async def post_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_news(context.application)
    await update.message.reply_text("📰 Новость опубликована вручную!")

# --- Основной запуск ---
def main():
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("post_now", post_now))

        # Настройка и запуск вебхука
        port = int(os.environ.get("PORT", 5000))
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=WEBHOOK_URL  # ← run_webhook сам установит вебхук!
        )

        # Установка вебхука для Telegram API
        #app.bot.set_webhook(f"{WEBHOOK_URL}")
        logging.info("✅ Вебхук успешно установлен")

    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
    news = get_latest_news()
    if news:
        print("📰", news["title"])
        print("🔗", news["link"])
        print("📝", news["summary"])
        print("🖼", news["image"])