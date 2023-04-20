import logging

from asyncpg import InvalidPasswordError
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError, DBConnectionError

from app.config import app_config

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f'postgres://{app_config().db.user}:'
    f'{app_config().db.password}@'
    f'{app_config().db.host}:'
    f'{app_config().db.port}/'
    f'{app_config().db.name}'
)

TORTOISE_ORM = {
    'connections': {'default': DATABASE_URL},
    'apps': {
        'models': {
            'models': ['app.store.database.models', 'aerich.models'],
            'default_connection': 'default',
        },
    },
}


async def database_initialization():
    try:
        await Tortoise.init(
            config=TORTOISE_ORM,
        )
    except (
            ConfigurationError, DBConnectionError, InvalidPasswordError
    ) as error:
        logger.error(error)
