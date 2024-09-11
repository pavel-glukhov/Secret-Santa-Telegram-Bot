import json
import logging
import os
from functools import lru_cache

from aioredis import Redis

from app.bot.languages.schemes import MainSchema, RootSchema

logger = logging.getLogger(__name__)


async def load_language_files_to_redis(directory: str, redis_client: Redis) -> None:
    await redis_client.delete('list_languages')
    await redis_client.delete('translations')
    
    translation_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                lang: dict = json.load(f)
                translation_dict.update(lang)
                await redis_client.rpush('list_languages', list(lang.keys())[0])
    
    await redis_client.set('translations', json.dumps(translation_dict, ensure_ascii=False))
    return None


@lru_cache
async def language_return_dataclass(redis_client: Redis) -> RootSchema:
    languages = await redis_client.get('translations')
    languages: dict = json.loads(languages.encode('utf-8'))
    
    languages_temp_dict = {}
    
    for key, value in languages.items():
        languages_temp_dict[key] = MainSchema(**value)
    
    root_scheme = RootSchema(languages=languages_temp_dict)
    
    return root_scheme
