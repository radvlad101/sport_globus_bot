# football_posting.py
import logging
from datetime import datetime

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

def calculate_probabilities(odds):
    """
    Рассчитывает вероятность исхода на основе коэффициентов.
    Возвращает словарь {'home': %, 'draw': %, 'away': %}.
    """
    try:
        p1, x, p2 = odds["homeWin"], odds["draw"], odds["awayWin"]
        inv_total = 1/p1 + 1/x + 1/p2
        prob_home = round((1/p1)/inv_total*100)
        prob_draw = round((1/x)/inv_total*100)
        prob_away = round((1/p2)/inv_total*100)
        return {"home": prob_home, "draw": prob_draw, "away": prob_away}
    except Exception as e:
        logging.error(f"[ERROR] Ошибка расчёта вероятности: {e}")
        return {"home": 0, "draw": 0, "away": 0}

import logging
from telegram.error import TelegramError

MAX_MESSAGE_LEN = 4096  # лимит Telegram

async def safe_send_message(bot, chat_id, text: str):
    """Безопасно отправляет сообщение в Telegram (режет, если > 4096)."""
    try:
        if len(text) <= MAX_MESSAGE_LEN:
            await bot.send_message(chat_id=chat_id, text=text)
            logging.info(f"[OK] Сообщение отправлено в {chat_id} (len={len(text)})")
        else:
            # разбиваем текст на части
            parts = [text[i:i + MAX_MESSAGE_LEN] for i in range(0, len(text), MAX_MESSAGE_LEN)]
            for idx, part in enumerate(parts, start=1):
                await bot.send_message(chat_id=chat_id, text=part)
                logging.info(f"[OK] Часть {idx}/{len(parts)} отправлена в {chat_id} (len={len(part)})")
    except TelegramError as e:
        logging.error(f"[FAIL] Ошибка при отправке в {chat_id}: {e}")


async def post_fixtures_with_odds(app, fixtures_data):
    """
    Асинхронно постит матчи с прогнозами/odds в Telegram.
    """
    for league_code, matches in fixtures_data.items():
        if not matches:
            logging.info(f"[DEBUG] Нет матчей для лиги {league_code}")
            continue

        league_name = LEAGUE_NAMES.get(league_code, league_code)
        logging.info(f"[DEBUG] Формируем пост для лиги {league_name} ({len(matches)} матчей)")

        caption_lines = [f"⚽ Ближайшие матчи — {league_name}\n"]

        for match in matches:
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            match_time = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            match_time_str = match_time.strftime("%d.%m %H:%M UTC")

            odds_text = ""
            prob_text = ""
            if "odds" in match:
                odds = match["odds"]
                odds_text = f"П1: {odds['homeWin']} X: {odds['draw']} П2: {odds['awayWin']}"
                probs = calculate_probabilities(odds)
                prob_text = f" | Вероятность: {home} {probs['home']}% - X {probs['draw']}% - {away} {probs['away']}%"

            caption_lines.append(
                f"{match_time_str} — {home} vs {away}\n{odds_text}{prob_text}\n"
            )

        caption = "\n".join(caption_lines)
        logging.debug(f"[DEBUG] Пост для {league_name}:\n{caption}")

        # 🔹 безопасная отправка
        await safe_send_message(app.bot, TELEGRAM_CHANNEL_ID, caption)
