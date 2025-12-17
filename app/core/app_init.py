import logging
from app.core.database.health import check_database

from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from app.bot.languages.loader import load_language_files_to_redis
from app.bot.loader import dp
from app.bot.register_middlewares import register_middlewares
from app.bot.register_routers import register_routers
from app.core.config.app_config import setup_logging
from app.core.redis import get_redis_client
from app.core.scheduler import scheduler
from app.core.config.app_config_validation import validate_room_length_value

logger = logging.getLogger(__name__)


async def init_application(config):
    setup_logging(config)
    validate_room_length_value(config)
    redis_ok = await load_languages_to_redis(config)
    db_ok = await check_database()

    if not redis_ok or not db_ok:
        if not redis_ok:
            logger.critical(
                "Application startup aborted: Redis dependency is unavailable"
            )
        if not db_ok:
            logger.critical(
                "Application startup aborted: PostgreSQL dependency is unavailable"
            )
        return
    register_routers(dp)
    register_middlewares(dp)

    scheduler.start()


async def load_languages_to_redis(config) -> bool:
    """Load language dicts to redis"""
    try:
        languages_folder = config.bot.language_folder
        await load_language_files_to_redis(
            languages_folder,
            get_redis_client()
        )
        logger.info("Languages successfully loaded into Redis.")
        return True
    except (RedisConnectionError, RedisError) as e:
        logger.critical(
            "Redis is unavailable. "
            "Make sure Redis is running and accessible at localhost:6379"
        )
        logger.debug("Redis error details", exc_info=e)
        return False
