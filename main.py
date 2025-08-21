import asyncio
import logging
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

# === Настройки ===
TELEGRAM_TOKEN = "8495882876:AAH1xwbeyOqPRkquvz7aijF5iHa6US3IgNg"
CHANNEL_ID = "@sport_globus"
AI21_API_KEY = "f46255e8-8dfb-4bdb-abf0-cc8eb4450cd0"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ====== Клиент AI21 ======
client = AI21Client(api_key=AI21_API_KEY)


# ====== Суммаризация через AI21 ======
async def summarize_text(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="jamba-large",
            messages=[
                ChatMessage(role="system", content="Ты — бот, делающий краткие спортивные суммаризации."),
                ChatMessage(role="user", content=f"Суммаризируй коротко спортивную новость:\n\n{text}\n\nКратко:")
            ],
            max_tokens=150
        )
        return response.output_text.strip()
    except Exception as e:
        logging.error(f"AI21 error: {e}")
        return None


# ====== Парсим sports.ru ======
async def fetch_latest_news():
    feed_url = "https://www.sports.ru/sports.xml"
    feed = feedparser.parse(feed_url)
    if feed.entries:
        entry = feed.entries[0]
        title = entry.title
        link = entry.link
        summary = await summarize_text(entry.summary)

        text = f"🏆 {title}\n\n"
        if summary:
            text += f"{summary}\n\n"
        else:
            text += "❌ Не удалось получить суммаризацию\n\n"
        text += f"🔗 Подробнее: {link}"

        return text
    return None


# ====== Публикуем в канал ======
async def post_latest_news():
    news = await fetch_latest_news()
    if news:
        await bot.send_message(CHANNEL_ID, news)


# ====== Команда /start ======
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я спорт-бот. Напиши /post_now чтобы запостить свежую новость.")


# ====== Команда /post_now ======
@dp.message(Command("post_now"))
async def cmd_post_now(message: types.Message):
    await message.answer("⏳ Беру свежую новость...")
    await post_latest_news()
    await message.answer("✅ Новость опубликована!")


# ====== Автопостинг раз в 1 день ======
async def auto_posting():
    while True:
        logging.info("Автопостинг: публикую новость...")
        await post_latest_news()
        await asyncio.sleep(24 * 60 * 60)  # ждать 1 день


# ====== Запуск ======
async def main():
    # Запускаем бота и автопостинг параллельно
    task_bot = asyncio.create_task(dp.start_polling(bot))
    task_auto = asyncio.create_task(auto_posting())
    await asyncio.gather(task_bot, task_auto)


if __name__ == "__main__":
    asyncio.run(main())
