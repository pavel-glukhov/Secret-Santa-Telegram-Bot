import json
import logging
import os
from functools import lru_cache

from redis import Redis
from pydantic import ValidationError

from app.bot.languages.schemes import TranslationMainSchema

logger = logging.getLogger(__name__)


async def load_language_files_to_redis(directory: str, redis_client: Redis) -> None:
    redis_client.delete('list_languages')
    language_selection_message = ''
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lang: dict = json.load(f)
                lang_name = list(lang.keys())[0]
                language_selection_message = language_selection_message + lang.get(
                    lang_name).get('messages').get('main_menu').get('language_selection')
                
                redis_client.set('language_selection_message', language_selection_message)
                redis_client.set(f'lang_{lang_name}', json.dumps(lang.get(lang_name), ensure_ascii=False))
                redis_client.rpush('list_languages', list(lang.keys())[0])
    return None


async def language_return_dataclass(redis_client: Redis, user_language: str) -> TranslationMainSchema:
    try:
        translation_str = redis_client.get(f'lang_{user_language}')
        translation: dict = json.loads(translation_str.encode('utf-8'))
        return TranslationMainSchema(**translation)
    
    except ValidationError as e:
        logger.error(e)
