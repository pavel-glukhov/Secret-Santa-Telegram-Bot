from aiogram import types

from app.database.config import async_session
from app.database.operations import RoomDB, UserDB


async def create_new_room(message: types.Message):
    async with async_session() as db_session:
        async with db_session.begin():
            user_db = UserDB(db_session)
            room_db = RoomDB(db_session)
            await room_db.create_room(name='sds', number=323232,
                                      owner_id=message.chat.id, budget='222')
