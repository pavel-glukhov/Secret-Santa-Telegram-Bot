import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT

from app.bot.loader import bot, dp
from app.bot.routers import register_routers
from app.config import ROOT_PATH, load_config, setup_logging, webhook_settings
from app.store.database import close_db, init_db
from app.store.scheduler import scheduler
from app.web.exceptions import app_exceptions
from app.web.routers import active_games, auth, main, rooms, users, webhooks
from app.web.schemes import AuthJWTSettings

logger = logging.getLogger(__name__)

exception_handlers = {
    401: app_exceptions.not_authenticated,
    403: app_exceptions.access_denied,
    404: app_exceptions.not_found_error,
    500: app_exceptions.internal_error,
}


async def on_startup():
    register_routers(dp)
    setup_logging()
    await init_db()
    scheduler.start()
    webhook_url = webhook_settings(load_config).get('webhook_url')
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != webhook_url:
        await bot.set_webhook(url=webhook_url)
    logger.info("App has been started")


async def on_shutdown():
    await bot.session.close()
    await close_db()
    logger.info("App has been stopped")


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


def init_fast_api_routers(app: FastAPI) -> None:
    app.include_router(main.router)
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(rooms.router)
    app.include_router(active_games.router)
    app.include_router(webhooks.router)


def init_fast_api_handlers(app: FastAPI) -> None:
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)


def create_app() -> FastAPI:
    app = FastAPI(debug=False,
                  exception_handlers=exception_handlers,
                  docs_url=None,
                  redoc_url=None)
    app.mount("/static",
              StaticFiles(directory=os.path.join(ROOT_PATH, "static")),
              name="static")
    init_fast_api_handlers(app)
    init_fast_api_routers(app)
    return app
