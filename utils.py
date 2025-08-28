#utils.py
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
from deep_translator import GoogleTranslator
import logging
from typing import List, Dict


from config import TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, AI21_API_KEY,WEBHOOK_URL, API_KEY_latest_news, strLeagueBadges

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai21_client = AI21Client(api_key=AI21_API_KEY)

def summarize_text(text: str) -> str:
    """Використовує AI21 для сумаризації тексту."""
    try:
        response = ai21_client.chat.completions.create(
            model="jamba-large-1.7",
            messages=[ChatMessage(role="user", content=f"Сделай краткое резюме этой новости:\n\n{text}")]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"AI21 помилка: {e}")
        return None



def translate_article_fields(
    article_data: dict,
    fields_to_translate: list[str],
    source_lang: str = 'auto',
    target_lang: str = 'ru'
) -> dict:
    """
    Переводит указанные поля статьи на целевой язык с обработкой ошибок

    Args:
        article_data (dict): Словарь с данными статьи
        fields_to_translate (list): Список полей для перевода
        source_lang (str): Исходный язык
        target_lang (str): Целевой язык

    Returns:
        dict: Словарь с переведенными полями
    """
    if not article_data or not fields_to_translate:
        return article_data

    translated_article = article_data.copy()
    translator = GoogleTranslator(source=source_lang, target=target_lang)

    for field in fields_to_translate:
        if field not in translated_article:
            logger.warning(f"Поле '{field}' отсутствует в данных")
            continue

        original_text = translated_article[field]

        # Пропускаем пустые значения
        if not original_text or not isinstance(original_text, str):
            continue

        try:
            translated_text = translator.translate(original_text)
            translated_article[field] = translated_text
            logger.info(f"Переведено поле '{field}': {original_text[:50]}... → {translated_text[:50]}...")

        except Exception as e:
            logger.error(f"Ошибка перевода поля '{field}': {e}")
            # Оставляем оригинальный текст

    return translated_article




def get_league_badge(leagues_data:List[Dict[str, str]],league_name: str,default: str = '') -> str:
    """
    Находит URL бейджа лиги без учета регистра.
    """
    if not leagues_data or not league_name:
        return default

    league_name_lower = league_name.lower()
    for league in leagues_data:
        if league.get('strLeague', '').lower() == league_name_lower:
            return league.get('strLeagueBadge', default)

    return default


