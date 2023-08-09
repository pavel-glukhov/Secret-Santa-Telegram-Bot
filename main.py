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

app = FastAPI(
    debug=False,
    exception_handlers=exception_handlers,
    docs_url=None,
    redoc_url=None
)

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

@app.on_event("startup")
async def on_startup():
    setup_logging()
    await init_db()
    scheduler.start()
    webhook_url = webhook_settings(load_config).get('webhook_url')
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != webhook_url:
        await bot.set_webhook(url=webhook_url)
    logger.info("App started")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    await close_db()
    logger.info("App stopped")


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
