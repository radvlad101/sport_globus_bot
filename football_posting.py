# football_posting.py
import logging
from datetime import datetime
from telegram import Bot

TELEGRAM_CHANNEL_ID = "@sport_globus"  # замените на ваш канал

LEAGUE_NAMES = {
    "PL": "АПЛ",
    "PD": "Ла Лига",
    "SA": "Серия А",
    "BL1": "Бундеслига",
    "FL1": "Лига 1",
    "CL": "Лига Чемпионов",
    "EL": "Лига Европы"
}
from datetime import datetime, timedelta, timezone

def filter_fixtures_next_week(fixtures_data, limit_matches):
    """
    Возвращает будущие матчи на ближайшие 7 дней, с ограничением по лигам.
    fixtures_data: dict с лигами -> списком матчей
    limit_matches: dict с лигами -> максимальное количество матчей
    """
    now = datetime.now(timezone.utc)
    next_week = now + timedelta(days=7)

    upcoming_fixtures = {}

    for league_code, matches in fixtures_data.items():
        future_matches = []

        for match in matches:
            match_time = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            if now <= match_time <= next_week:
                future_matches.append(match)

        # Ограничиваем по количеству матчей
        max_count = limit_matches.get(league_code, len(future_matches))
        upcoming_fixtures[league_code] = future_matches[:max_count]

    return upcoming_fixtures



async def safe_send_message(bot: Bot, chat_id: str, text: str):
    """
    Безопасная отправка сообщения с логированием ошибок.
    """
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logging.info("[INFO] Сообщение успешно отправлено")
    except Exception as e:
        logging.error(f"[ERROR] Ошибка при отправке сообщения: {e}")


async def post_fixtures_with_odds(app, fixtures_data):
    """
    Асинхронно постит матчи с прогнозами/odds в Telegram.
    fixtures_data: dict с лигами -> списком матчей
    """
    for league_code, matches in fixtures_data.items():
        if not matches:
            logging.info(f"[DEBUG] Нет матчей для лиги {league_code}")
            continue

        league_name = LEAGUE_NAMES.get(league_code, league_code)
        logging.info(f"[DEBUG] Начинаем формирование поста для лиги {league_name} ({len(matches)} матчей)")

        caption_lines = [f"⚽ Ближайшие матчи — {league_name}\n"]

        for match in matches:
            # Проверяем, что match это dict
            if not isinstance(match, dict):
                logging.warning(f"[WARN] Неверный формат матча: {match}")
                continue

            home = match.get("homeTeam", {}).get("name", "Unknown")
            away = match.get("awayTeam", {}).get("name", "Unknown")
            utc_date = match.get("utcDate", "Unknown date")

            # Преобразуем дату в читаемый формат
            try:
                match_time = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
                match_time_str = match_time.strftime("%d.%m %H:%M UTC")
            except Exception:
                match_time_str = utc_date

            # Безопасная обработка odds
            odds = match.get("odds", {})
            if "homeWin" in odds and "draw" in odds and "awayWin" in odds:
                odds_text = f"П1: {odds['homeWin']} X: {odds['draw']} П2: {odds['awayWin']}"
            else:
                odds_text = "Коэффициенты недоступны (только платный план)"

            caption_lines.append(f"{match_time_str} — {home} vs {away}\n{odds_text}\n")

        # Составляем весь пост
        caption = "\n".join(caption_lines)
        logging.debug(f"[DEBUG] Пост для {league_name}:\n{caption}")

        # Отправка в Telegram
        await safe_send_message(app.bot, TELEGRAM_CHANNEL_ID, caption)
