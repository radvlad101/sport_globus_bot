import feedparser
from openai import OpenAI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import logging
import os

# 🔹 Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sport_globus")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # например: https://mybot.onrender.com
PORT = int(os.getenv("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Получаем новости из RSS
async def get_sports_news():
    feed = feedparser.parse("https://www.sports.ru/rss/all_news.xml")
    return feed.entries[:1]

# --- Краткое резюме через OpenAI
async def summarize_news(text: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Сделай краткий пересказ спортивной новости:\n{text}"}],
        max_tokens=150
    )
    return response.choices[0].message.content

# --- Постинг в канал
async def post_news():
    news_list = await get_sports_news()
    for entry in news_list:
        summary = await summarize_news(entry.summary)
        msg = f"🏆 {entry.title}\n\n{summary}\n\n🔗 Подробнее: {entry.link}"
        await bot.send_message(CHANNEL_ID, msg)

# --- Команда для ручного постинга
@dp.message(Command("post_now"))
async def manual_post(message: types.Message):
    await post_news()
    await message.answer("✅ Пост сделан вручную!")

# --- Scheduler (раз в сутки пост)
async def scheduler():
    while True:
        await post_news()
        await asyncio.sleep(24 * 60 * 60)

# --- Запуск webhook-сервера
async def on_startup(app: web.Application):
    # Устанавливаем webhook
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    # Сообщаем в канал, что бот запущен
    await bot.send_message(CHANNEL_ID, "🤖 Бот успешно запущен и готов работать!")

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)

    # Фоновая задача (постим раз в день)
    asyncio.create_task(scheduler())

    web.run_app(app, port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
