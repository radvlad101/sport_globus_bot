import feedparser
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import logging

# 🔹 Настройки
TELEGRAM_TOKEN = "8495882876:AAFkTpIJyLjwsV47aMqwSkB5UHcz7810Ckk"
CHANNEL_ID = "@sport_globus"
openai.api_key = "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"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🔹 Получаем новости из RSS
async def get_sports_news():
    url = "https://www.sports.ru/rss/all_news.xml"
    feed = feedparser.parse(url)
    return feed.entries[:1]  # берём только одну свежую новость

# 🔹 Делаем краткое резюме через OpenAI
async def summarize_news(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Сделай краткий пересказ спортивной новости:\n{text}"}],
        max_tokens=150
    )
    return response.choices[0].message["content"]

# 🔹 Постинг в канал с изображением
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

# 🔹 Команда для ручного постинга
@dp.message(Command("post_now"))
async def manual_post(message: types.Message):
    await post_news()
    await message.answer("✅ Пост сделан вручную!")

# 🔹 Запуск раз в сутки
async def scheduler():
    while True:
        await post_news()
        await asyncio.sleep(24 * 60 * 60)  # ждать 1 день


async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
