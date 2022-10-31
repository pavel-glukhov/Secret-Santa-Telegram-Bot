import logging

from asyncpg import InvalidPasswordError
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError, DBConnectionError

from app.config import config
from app.store.database.queries.rooms import RoomDB
from app.store.database.queries.users import UserDB
from app.store.database.queries.wishes import WishDB

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f'postgres://{config.db.user}:'
    f'{config.db.password}@'
    f'{config.db.host}:'
    f'{config.db.port}/'
    f'{config.db.name}'
)

TORTOISE_ORM = {
    'connections': {'default': DATABASE_URL},
    'apps': {
        'models': {
            'models': ['app.database.models', 'aerich.models'],
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


user_db = UserDB
room_db = RoomDB
wish_db = WishDB
