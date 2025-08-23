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


import logging

async def safe_send_message(app, chat_id, text):
    """Безопасная отправка сообщений с логированием ошибок"""
    try:
        await app.bot.send_message(chat_id=chat_id, text=text)
        logging.info("[DEBUG] Сообщение успешно отправлено в %s", chat_id)
    except Exception as e:
        logging.error("[ERROR] Ошибка при отправке сообщения в %s: %s", chat_id, e)


async def post_fixtures_with_odds(app, fixtures_data):
    """Формируем и постим список матчей с коэффициентами"""
    logging.info("[DEBUG] Начинаем формирование поста (матчей: %s)", len(fixtures_data))

    post_lines = []
    missing_odds_count = 0

    for match in fixtures_data:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        utc_date = match["utcDate"]

        # Коэффициенты
        if "odds" in match and match["odds"]:
            odds = match["odds"]

            home_odds = odds.get("homeWin", "—")
            draw_odds = odds.get("draw", "—")
            away_odds = odds.get("awayWin", "—")

            odds_text = f"П1: {home_odds} X: {draw_odds} П2: {away_odds}"

            # Если все три коэффициента есть → считаем вероятность
            if all(isinstance(x, (int, float)) for x in [home_odds, draw_odds, away_odds]):
                probs = calculate_probabilities(odds)
                prob_text = (
                    f" | Вероятность: {home} {probs['home']}% - "
                    f"X {probs['draw']}% - {away} {probs['away']}%"
                )
            else:
                prob_text = ""
                missing_odds_count += 1

        else:
            odds_text = "Коэффициенты пока не доступны"
            prob_text = ""
            missing_odds_count += 1

        post_lines.append(f"{home} vs {away} ({utc_date})\n{odds_text}{prob_text}")

    # Сборка поста
    post_text = "⚽ Ближайшие матчи:\n\n" + "\n\n".join(post_lines)

    # Логируем инфо
    logging.info("[DEBUG] Пост сформирован. Всего матчей: %s | Без коэффициентов: %s",
                 len(fixtures_data), missing_odds_count)

    # Отправка в канал
    await safe_send_message(app, "@sport_globus", post_text)

