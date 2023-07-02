import logging

from tortoise import Tortoise

from app.config import load_config

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f'postgres://{load_config().db.user}:'
    f'{load_config().db.password}@'
    f'{load_config().db.host}:'
    f'{load_config().db.port}/'
    f'{load_config().db.name}'
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

async def init_db() -> None:
    await Tortoise.init(
        config=TORTOISE_ORM
    )

async def close_db() -> None:
    await Tortoise.close_connections()