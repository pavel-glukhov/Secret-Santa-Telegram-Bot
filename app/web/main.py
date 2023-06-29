import asyncio
import logging.config
import os

import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from app.config import load_config, root_path
from app.store.database import TORTOISE_ORM
from app.store.scheduler import scheduler
from app.web.exceptions import app_exceptions
from app.web.routers import active_games, auth, general, rooms, users

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

# TODO Временный логгер
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

scheduler.start()
setup_logging()
# TODO Временный регистратор
register_tortoise(
    app,
    config=TORTOISE_ORM,
)
