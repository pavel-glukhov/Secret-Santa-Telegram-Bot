import logging.config
import os

import uvicorn

import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from app.bot import bot
from app.config import load_config, root_path, webhook_settings
from app.store.database import TORTOISE_ORM
from app.store.scheduler import scheduler
from app.web.exceptions import app_exceptions
from app.web.routers import active_games, auth, general, rooms, users, webhooks

logger = logging.getLogger(__name__)

exception_handlers = {
    401: app_exceptions.not_authenticated,
    403: app_exceptions.access_denied,
    404: app_exceptions.not_found_error,
    500: app_exceptions.internal_error,
}
app = FastAPI(debug=True, exception_handlers=exception_handlers)
app.mount("/static", StaticFiles(directory=os.path.join(root_path, "static")),
          name="static")

app.include_router(general.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(active_games.router)
app.include_router(webhooks.router)


async def db_init():
    register_tortoise(
        app,
        config=TORTOISE_ORM,
    )


def setup_logging() -> None:
    config = load_config()
    configuration_file = os.path.join(root_path, config.log.config_file)
    
    with open(configuration_file, 'r') as stream:
        logging_cfg = yaml.load(stream, Loader=yaml.FullLoader)
    
    logging_cfg['handlers'][
        'timed_rotating_handler']['filename'] = os.path.join(
        config.log.log_path,
        config.log.log_file
    )
    logging.config.dictConfig(logging_cfg)


@app.on_event("startup")
async def on_startup():
    setup_logging()
    await db_init()
    scheduler.start()
    webhook_url = webhook_settings(load_config).get('webhook_url')
    webhook_info = await bot.get_webhook_info()
    
    if webhook_info.url != webhook_url:
        await bot.set_webhook(url=webhook_url)
    logger.info("App started")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    logger.info("App stopped")


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
