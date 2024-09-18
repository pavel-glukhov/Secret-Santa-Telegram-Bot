import logging

from fastapi import FastAPI

from app.store.redis import get_redis_client
from app.bot.languages import load_language_files_to_redis
from app.bot.loader import bot, dp
from app.bot.register_middlewares import register_middlewares
from app.bot.register_routers import register_routers
from app.config import load_config, setup_logging, webhook_settings
from app.store.scheduler import scheduler
from app.web.register_routers import register_fastapi_routers

logger = logging.getLogger(__name__)


async def on_startup():
    languages_folder = load_config().bot.language_folder
    await load_language_files_to_redis(languages_folder, get_redis_client())
    logger.info("Data from languages folder have been loaded to Redis.")
    
    register_routers(dp)
    register_middlewares(dp)
    
    setup_logging()
    scheduler.start()
    
    webhook_url = webhook_settings(load_config).get('webhook_url')
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != webhook_url:
        await bot.set_webhook(url=webhook_url)
    logger.info("App has been started")


async def on_shutdown():
    await bot.session.close()
    logger.info("App has been stopped")


def init_fast_api_handlers(app: FastAPI) -> None:
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)


def create_app() -> FastAPI:
    app = FastAPI(debug=False,
                  docs_url=None,
                  redoc_url=None)
    init_fast_api_handlers(app)
    register_fastapi_routers(app)
    return app
