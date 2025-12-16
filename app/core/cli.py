import logging
from app.core.database.health import check_database
from aiogram.exceptions import TelegramAPIError
from fastapi import FastAPI
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from app.bot.languages.loader import load_language_files_to_redis
from app.bot.loader import bot, dp
from app.bot.register_middlewares import register_middlewares
from app.bot.register_routers import register_routers
from app.core.config.app_config import load_config, setup_logging, webhook_settings
from app.core.redis import get_redis_client
from app.core.scheduler import scheduler
from app.web.register_routers import register_fastapi_routers
from app.core.config.app_config_validation import validate_room_length_value
logger = logging.getLogger(__name__)


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


async def setup_webhook(config) -> None:
    """Set up the Telegram webhook if it differs from the configured URL."""
    try:

        webhook_url = webhook_settings(config).get('webhook_url')
        if not webhook_url:
            logger.error("Webhook URL is not configured")
            raise ValueError("Webhook URL is missing in configuration")
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhook_url:
            await bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set to {webhook_url}")
        else:
            logger.info(f"Webhook already set to {webhook_url}")
    except TelegramAPIError as e:
        logger.error(f"Failed to set webhook: {str(e)}")
        raise


async def on_startup():
    config = load_config()
    setup_logging(config)

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

    try:
        register_routers(dp)
        register_middlewares(dp)

        scheduler.start()
        await setup_webhook(config)

        logger.info("Application started successfully")

    except TelegramAPIError as e:
        logger.critical("Application startup failed: Telegram API error")
        logger.debug("Telegram error details", exc_info=e)
        return


async def on_shutdown():
    await bot.session.close()
    logger.info("Application shutdown completed")


def register_event_handlers(app: FastAPI) -> None:
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)


def configure_fastapi() -> FastAPI:
    app = FastAPI(debug=True, docs_url=None, redoc_url=None)
    register_event_handlers(app)
    register_fastapi_routers(app)
    return app


def create_app() -> FastAPI:
    validate_room_length_value(load_config())
    return configure_fastapi()
