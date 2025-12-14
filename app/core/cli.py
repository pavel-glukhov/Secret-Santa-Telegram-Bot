import logging

from aiogram.exceptions import TelegramAPIError
from fastapi import FastAPI
from redis import RedisError

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


async def load_languages_to_redis(config) -> None:
    """Load language files from the configured folder into Redis."""
    try:
        languages_folder = config.bot.language_folder
        await load_language_files_to_redis(languages_folder, get_redis_client())
        logger.info("Data from languages folder have been loaded to Redis.")
    except RedisError as e:
        logger.error(f"Failed to load languages to Redis: {str(e)}")
        raise


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
    try:
        config = load_config()
        setup_logging(config)
        await load_languages_to_redis(config)
        register_routers(dp)
        register_middlewares(dp)
        scheduler.start()
        await setup_webhook(config)
        logger.info("App has been started")
    except  ConnectionError as e:
        logger.error(f"Failed to start app: {str(e)}")


async def on_shutdown():
    await bot.session.close()
    logger.info("App has been stopped")


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
