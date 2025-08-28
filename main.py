#main.py

import logging
import os
from aiogram import Bot, Dispatcher,Router, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiogram.types import Message
from datetime import date, timedelta

# Импорты со своих модулей
from  utils import summarize_text, translate_article_fields, get_league_badge
from football_api import get_latest_news, get_events_by_sport_and_date
from football_posting import post_news, post_fixtures
from config import TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, AI21_API_KEY,WEBHOOK_URL, API_KEY_latest_news, strLeagueBadges


# --- Configuration ---
#TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
#WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = Router()



@router.message(Command("post_news_now"))
async def post_news_now(message: Message, bot: Bot):
    #def get_latest_news(language="ru")-> Dict[str, Any]:
    news_ru = get_latest_news(language="ru")
    news_en = get_latest_news(language="en")
    news_en_ru = translate_article_fields (news_en,['title',"summary"],'en','ru')
    await post_news(bot, TELEGRAM_CHANNEL_ID, news_ru)
    await post_news(bot, TELEGRAM_CHANNEL_ID, news_en_ru)
    await message.reply("Новини будуть опубліковані!")



@router.message(Command("post_fixtures_now"))
async def post_fixtures_now(message: Message, bot: Bot):

    sport ='soccer_epl'
    date_event = date.today() + timedelta(days=2)
    #def get_events_by_sport_and_date(sport: str, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    events = get_events_by_sport_and_date(sport, date_event, date_event)

    #def get_league_badge(leagues_data: List[Dict[str, str]], league_name: str, default: str = '') -> str:
    str_league_badge = get_league_badge (strLeagueBadges,sport)

    #async def post_fixtures(bot: Bot, telegram_channel_id: str, events: list, str_league_badge: str):
    await post_fixtures(bot,TELEGRAM_CHANNEL_ID, events, str_league_badge)
    await message.reply("Розклад матчів буде опубліковано!")


# --- Main function ---
async def main():
    """Main function to start the bot with a webhook."""
    # Ensure token and webhook URL are set
    if not TELEGRAM_TOKEN or not WEBHOOK_URL:
        logger.error("❌ TELEGRAM_TOKEN or WEBHOOK_URL environment variables are not set.")
        return

    # Initialize bot and dispatcher
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Register handlers
    dp.message.register(post_news_now, Command("post_news_now"))
    dp.message.register(post_fixtures_now, Command("post_fixtures_now"))

    # Webhook setup
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        #secret_token=TELEGRAM_TOKEN,  # It's good practice to use a secret token
    )

    # Register handlers on the web server
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    # Start the web server
    port = int(os.environ.get("PORT", 5000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)

    # Set the webhook URL on the Telegram side
    await bot.set_webhook(url=WEBHOOK_URL)

    logger.info("✅ Бот успішно запущено!")

    # Keep the server running
    await site.start()

    # Wait for signals to gracefully shut down
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await bot.delete_webhook()  # Clean up webhook on shutdown
        await runner.cleanup()

    logger.info("✅ Бот зупинено.")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")