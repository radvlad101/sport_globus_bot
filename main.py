import os
import feedparser
import logging
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@sport_globus")
AI21_API_KEY = os.getenv("AI21_API_KEY")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# --- функции постинга ---
async def get_sports_news():
    feed = feedparser.parse("https://www.sports.ru/rss/all_news.xml")
    return feed.entries[:1]

async def summarize_news(text: str):
    url = "https://api.ai21.com/studio/v1/j1-large/complete"
    headers = {"Authorization": f"Bearer {AI21_API_KEY}"}
    data = {"prompt": f"Сделай краткий пересказ:\n{text}", "maxTokens": 150}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers)
        return resp.json()['completions'][0]['data']['text']

async def post_news():
    news_list = await get_sports_news()
    for entry in news_list:
        summary = await summarize_news(entry.summary)
        image_url = entry.get('media_content', [{'url': None}])[0]['url']
        msg = f"🏆 {entry.title}\n\n{summary}\n\n🔗 Подробнее: {entry.link}"
        if image_url:
            await bot.send_photo(CHANNEL_ID, photo=image_url, caption=msg)
        else:
            await bot.send_message(CHANNEL_ID, msg)

# --- ручной пост ---
@dp.message(Command("post_now"))
async def manual_post(message: types.Message):
    await post_news()
    await message.answer("✅ Пост сделан вручную!")

# --- aiohttp для Render ---
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    web.run_app(app, port=PORT)

if __name__ == "__main__":
    import asyncio
    from aiohttp import web
    # запускаем web-приложение напрямую
    app = web.Application()
    # регистрируем webhook
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    # запуск webhook
    app.on_startup.append(lambda app: bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH))
    web.run_app(app, port=PORT)

