import logging
import os

import uvicorn

from app.bot import bot
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT

from app.config import load_config, ROOT_PATH, webhook_settings, setup_logging
from app.store.database import init_db, close_db
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

@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


def create_app() -> FastAPI:
    app = FastAPI(
        debug=False,
        exception_handlers=exception_handlers,
        docs_url=None,
        redoc_url=None
    )
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(ROOT_PATH, "static")),
        name="static"
    )

    app.include_router(main.router)
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(rooms.router)
    app.include_router(active_games.router)
    app.include_router(webhooks.router)
    return app

async def on_startup():
    try:
        setup_logging()
        await init_db()
        scheduler.start()
        webhook_url = webhook_settings(load_config).get('webhook_url')
        webhook_info = await bot.get_webhook_info()
    
        if webhook_info.url != webhook_url:
            await bot.set_webhook(url=webhook_url)
            
    except Exception as ex:
        logger.error(ex)
    logger.info("App has been started")

async def on_shutdown():
    await bot.session.close()
    await close_db()
    logger.info("App has been stopped")


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, port=8000)
