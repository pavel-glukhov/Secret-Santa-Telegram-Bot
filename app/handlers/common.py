from app import dispatcher as dp
from aiogram import types
from app.database.operations import UserDB, RoomDB
from app.database.config import async_session

from app.keyborads.common import create_common_keyboards


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name

    async with async_session() as db_session:
        async with db_session.begin():
            await UserDB(db_session).create_if_not_exist(username,
                                                         user_id,
                                                         first_name,
                                                         last_name)

            rooms = await RoomDB(db_session).get_joined_in_rooms(user_id)

    keyboard = await create_common_keyboards(rooms)

    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Об игре ℹ️")
async def about_game(message: types.Message):
    msg = 'Это адаптированная игра "Тайный Санта"'
    await message.answer(msg)
