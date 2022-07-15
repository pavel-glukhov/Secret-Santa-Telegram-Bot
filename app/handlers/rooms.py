from aiogram import types

from app.database.config import async_session
from app.database.operations import RoomDB, UserDB
from app import dispatcher as dp, bot


@dp.message_handler(lambda message: message.text == "Создать комнату 🔨")
async def create_room(message: types.Message):
    await message.answer('Нажата кнопка "Создать комнату 🔨"')


@dp.message_handler(lambda message: message.text == "Войти в комнату 🏠")
async def join_room(message: types.Message):
    await message.answer('Нажата кнопка "Создать комнату 🔨"')


async def create_new_room(message: types.Message):
    async with async_session() as db_session:
        async with db_session.begin():
            room_db = RoomDB(db_session)
            await room_db.create_room(name='sds', number=323232,
                                      owner_id=message.chat.id, budget='222')
