import asyncio
import os
import yaml
import logging.config

from fastapi import FastAPI
from app.store.database import TORTOISE_ORM
from app.web.routers import auth, users, general, rooms
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from app.web.exceptions import app_exceptions
from app.config import root_path, load_config

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


setup_logging()
# TODO Временный регистратор
register_tortoise(
    app,
    config=TORTOISE_ORM,
)
