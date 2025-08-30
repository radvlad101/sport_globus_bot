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



"""
from aiogram import Bot
from aiogram.types import InputMediaPhoto
from typing import List, Dict
import html
import logging

# Создаём собственный логер
logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)  # можно DEBUG для подробной отладки

# Настройка обработчика (вывод в консоль)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)"""


async def post_fixtures(bot: Bot, telegram_channel_id: str, events: List[Dict], banner: str):
    """
    Отправляет посты о предстоящих матчах в Telegram-канал.

    Args:
        bot (Bot): Объект бота aiogram.
        telegram_channel_id (str): ID Telegram-канала.
        events (List[Dict]): Список матчей.
        banner (str): URL баннера события.
    """
    for event in events:
        home_team = event.get('home_team', 'N/A')
        away_team = event.get('away_team', 'N/A')
        commence_time = event.get('commence_time', 'N/A')

        # Проверка баннера
        banner_url = banner if banner and banner.startswith("http") else None

        # Собираем информацию о коэффициентах
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

        # Формируем текст сообщения
        message_text = (
            f"<b>Матч:</b> {html.escape(home_team)} vs {html.escape(away_team)}\n"
            f"<b>Время начала:</b> {html.escape(commence_time.replace('T', ' ').replace('Z', ' UTC'))}\n"
            f"-----------------------------------\n"
            f"{odds_text}"
        )

        try:
            # Отправляем баннер, если он есть
            if banner_url:
                await bot.send_photo(
                    chat_id=telegram_channel_id,
                    photo=banner_url,
                    caption=f"🗓️ Предстоящий матч: {home_team} vs {away_team}"
                )
                logger.info(f"Отправлен баннер для {home_team} vs {away_team}")
            else:
                # Если баннера нет — fallback
                await bot.send_message(
                    chat_id=telegram_channel_id,
                    text=f"⚽️ {home_team} vs {away_team}"
                )
                logger.warning(f"Нет баннера для {home_team} vs {away_team}")

            # Отправляем подробное сообщение с коэффициентами
            await bot.send_message(
                chat_id=telegram_channel_id,
                text=message_text,
                parse_mode="HTML"
            )
            logger.info(f"Отправлено сообщение с коэффициентами для {home_team} vs {away_team}")

        except Exception as e:
            logger.error(f"Не удалось отправить событие в Telegram: {e}")







































"""
async def post_fixtures(bot: Bot, telegram_channel_id: str, events: List[Dict], str_league_badge: str):
    """
"""
    Отправляет посты о предстоящих матчах в Telegram-канал.

    Args:
        bot (Bot): Объект бота aiogram.
        telegram_channel_id (str): ID Telegram-канала.
        events (List[Dict]): Список матчей.
        str_league_badge (str): URL эмблемы лиги.
    """
"""
    for event in events:
        home_team = event.get('home_team', 'N/A')
        away_team = event.get('away_team', 'N/A')
        commence_time = event.get('commence_time', 'N/A')

        # Проверка бейджей
        home_badge = event.get('home_team_badge')
        away_badge = event.get('away_team_badge')

        home_badge = home_badge if home_badge and home_badge.startswith("http") else "⚽️"
        away_badge = away_badge if away_badge and away_badge.startswith("http") else "⚽️"
        league_badge = str_league_badge if str_league_badge and str_league_badge.startswith("http") else "⚽️"

        # Собираем информацию о коэффициентах
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

        # Формируем текст сообщения
        message_text = (
            f"<b>Матч:</b> {html.escape(home_team)} vs {html.escape(away_team)}\n"
            f"<b>Время начала:</b> {html.escape(commence_time.replace('T', ' ').replace('Z', ' UTC'))}\n"
            f"-----------------------------------\n"
            f"{odds_text}"
        )

        # Подготавливаем медиа для отправки
        media = []
        if league_badge != "⚽️":
            media.append(InputMediaPhoto(media=league_badge, caption=f"🗓️ Предстоящий матч: {home_team} vs {away_team}"))
        if home_badge != "⚽️":
            media.append(InputMediaPhoto(media=home_badge))
        if away_badge != "⚽️":
            media.append(InputMediaPhoto(media=away_badge))

        try:
            # Отправляем медиа-группу, если есть хотя бы одно изображение
            if media:
                await bot.send_media_group(chat_id=telegram_channel_id, media=media)
            else:
                # Если нет изображений, просто отправляем текст
                await bot.send_message(chat_id=telegram_channel_id, text=f"⚽️ {home_team} vs {away_team}")

            # Отправляем подробное сообщение с коэффициентами
            await bot.send_message(chat_id=telegram_channel_id, text=message_text, parse_mode="HTML")

        except Exception as e:
            print(f"Не удалось отправить событие в Telegram: {e}")




#async def post_fixtures( context: ContextTypes.DEFAULT_TYPE, TELEGRAM_CHANNEL_ID ,events, strLeagueBadge):

async def post_fixtures(bot: Bot, telegram_channel_id: str, events: List[Dict], str_league_badge: str):
    """
"""
    Отправляет посты о предстоящих матчах в Telegram-канал, используя aiogram.

    Args:
        bot (Bot): Объект бота aiogram.
        telegram_channel_id (str): ID Telegram-канала.
        events (List[Dict]): Список словарей, каждый из которых представляет предстоящий матч.
        str_league_badge (str): URL-адрес эмблемы лиги.
    """
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
            print(f"Не удалось отправить событие в Telegram: {e}")"""