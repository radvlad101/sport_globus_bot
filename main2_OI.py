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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # типа https://mybot.onrender.com/webhook
PORT = int(os.getenv("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)


# --- функции постинга
async def get_sports_news():
    feed = feedparser.parse("https://www.sports.ru/rss/all_news.xml")
    return feed.entries[:1]

async def summarize_news(text: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Сделай краткий пересказ:\n{text}"}],
        max_tokens=150
    )
    return response.choices[0].message.content

async def post_news():
    news_list = await get_sports_news()
    for entry in news_list:
        summary = await summarize_news(entry.summary)
        msg = f"🏆 {entry.title}\n\n{summary}\n\n🔗 Подробнее: {entry.link}"
        await bot.send_message(CHANNEL_ID, msg)


# --- обработчик команды /post_now
@dp.message(Command("post_now"))
async def manual_post(message: types.Message):
    await post_news()
    await message.answer("✅ Пост сделан вручную!")


# 🔹 aiohttp-приложение для Render
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)

    # запускаем фонового планировщика
    async def scheduler():
        while True:
            await post_news()
            await asyncio.sleep(24 * 60 * 60)

    asyncio.create_task(scheduler())


def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)

    web.run_app(app, port=PORT)


if __name__ == "__main__":
    main()
