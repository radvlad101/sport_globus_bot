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

# --- Функция получения новости ---
def get_latest_news():
    feed_url = "https://www.sports.ru/rss/all_news.xml"
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        logging.error("❌ Нет новостей в RSS")
        return None
    item = feed.entries[0]
    return {"title": item.title, "link": item.link, "summary": item.get("summary", "")}

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

# --- Постинг новости ---
async def post_news(app: Application):
    news = get_latest_news()
    if not news:
        return
    summary = summarize_text(news["summary"] or news["title"])
    if not summary:
        summary = "❌ Не удалось получить суммаризацию."
    message = f"📰 {news['title']}\n\n{summary}\n\n🔗 Подробнее: {news['link']}"
    try:
        await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)
        logging.info("✅ Новость опубликована")
    except Exception as e:
        logging.error(f"Ошибка публикации: {e}")

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