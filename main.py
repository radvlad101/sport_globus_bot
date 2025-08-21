import os
import logging
import feedparser
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import telegram
print(telegram.__version__)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # например "@mychannel"
AI21_API_KEY = os.getenv("AI21_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # например https://mydomain.com/webhook

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
        return response.outputs[0].content[0].text.strip()
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
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Команда для ручного постинга
    app.add_handler(CommandHandler("post_now", post_now))

    # Вебхук вместо polling
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
