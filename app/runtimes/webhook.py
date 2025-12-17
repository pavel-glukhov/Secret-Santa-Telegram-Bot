import logging
from aiogram.exceptions import TelegramAPIError
from fastapi import FastAPI

from app.bot.loader import bot
from app.core.app_init import init_application

from app.core.config.app_config import load_config, webhook_settings

from app.web.register_routers import register_fastapi_routers

logger = logging.getLogger(__name__)

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

    try:
        await init_application(config)
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
    return configure_fastapi()

