#football_posting.py
import logging
import html
from typing import List, Dict
from aiogram import Bot
from aiogram.types import InputMediaPhoto



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_news(bot,TELEGRAM_CHANNEL_ID,article_data):

    logging.info("Attempting to get news...")

    if article_data:
        logging.info("news found. Attempting to post...")
        caption = f"📰 {article_data['title']}\n\n{article_data['summary']}\n\n🔗 Подробнее: {article_data['link']}"
        try:
            if article_data.get("image"):
                await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=article_data["image"], caption=caption)
            else:
                await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=caption)
            logging.info("news posted successfully.")
        except Exception as e:
            logging.error(f"Error posting news: {e}")
    else:
        logging.warning("Nonews found.")




#async def post_fixtures( context: ContextTypes.DEFAULT_TYPE, TELEGRAM_CHANNEL_ID ,events, strLeagueBadge):

async def post_fixtures(bot: Bot, telegram_channel_id: str, events: List[Dict], str_league_badge: str):
    """
    Отправляет посты о предстоящих матчах в Telegram-канал, используя aiogram.

    Args:
        bot (Bot): Объект бота aiogram.
        telegram_channel_id (str): ID Telegram-канала.
        events (List[Dict]): Список словарей, каждый из которых представляет предстоящий матч.
        str_league_badge (str): URL-адрес эмблемы лиги.
    """
    for event in events:
        home_team = event.get('home_team', 'N/A')
        away_team = event.get('away_team', 'N/A')
        commence_time = event.get('commence_time', 'N/A')

        # Get team badges, handling cases where they might be missing
        home_badge = event.get('home_team_badge') or 'https://example.com/placeholder.png'
        away_badge = event.get('away_team_badge') or 'https://example.com/placeholder.png'

        # Gather information about bookmakers and odds
        bookmakers = event.get('bookmakers', [])
        odds_text = ""
        if bookmakers:
            for bm in bookmakers:
                bm_title = bm.get('title', 'N/A')
                odds_text += f"<b>{html.escape(bm_title)}:</b>\n"
                markets = bm.get('markets', [])
                if markets:
                    for market in markets:
                        if market.get('key') == 'h2h':
                            outcomes = market.get('outcomes', [])
                            for outcome in outcomes:
                                name = outcome.get('name', 'N/A')
                                price = outcome.get('price', 'N/A')
                                odds_text += f"  • {html.escape(name)}: {price}\n"
                odds_text += "\n"

        # Prepare the photo album
        media = [
            InputMediaPhoto(
                media=str_league_badge,
                caption=f"🗓️ Предстоящий матч:\n{html.escape(home_team)} vs {html.escape(away_team)}"
            ),
            InputMediaPhoto(media=home_badge),
            InputMediaPhoto(media=away_badge)
        ]

        # Prepare the message text
        message_text = (
            f"<b>Матч:</b> {html.escape(home_team)} vs {html.escape(away_team)}\n"
            f"<b>Время начала:</b> {html.escape(commence_time.replace('T', ' ').replace('Z', ' UTC'))}\n"
            f"-----------------------------------\n"
            f"{odds_text}"
        )

        try:
            # Send the media group (league badge + team badges)
            await bot.send_media_group(chat_id=telegram_channel_id, media=media)

            # Send the detailed message with odds
            await bot.send_message(
                chat_id=telegram_channel_id,
                text=message_text,
                parse_mode="HTML"
            )

        except Exception as e:
            print(f"Не удалось отправить событие в Telegram: {e}")