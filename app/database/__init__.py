from tortoise import Tortoise

from app.database.operations.room_model import RoomDB
from app.database.operations.user_model import UserDB
from app.database.operations.wish_model import WishDB

from app.config import config

DATABASE_URL = f'postgres://{config.db.user}:'\
               f'{config.db.password}@{config.db.host}:{config.db.port}/' \
               f'{config.db.name}'

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
    await Tortoise.init(
        config=TORTOISE_ORM,
    )


user_db = UserDB
room_db = RoomDB
wish_db = WishDB
