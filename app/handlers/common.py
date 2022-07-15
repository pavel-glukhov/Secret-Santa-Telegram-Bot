from aiogram.dispatcher.filters import Text

from app import dispatcher as dp, bot
from aiogram import types
from app.database.operations import UserDB, RoomDB
from app.database.config import async_session
import logging
from aiogram.types.message import ParseMode

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users_list_rooms = []

    async with async_session() as db_session:
        async with db_session.begin():
            user_db = UserDB(db_session)
            telegram_user = await user_db.get_user(user_id=user_id)
            logging.info(message.chat)
            if not telegram_user:
                logging.info(f'INFO: create new user: {user_id}')
                await user_db.create_user(
                    username=message.chat.username,
                    user_id=message.chat.id,
                    first_name=message.chat.first_name,
                    last_name=message.chat.last_name
                )

            rooms = await RoomDB(db_session).get_joined_rooms(user_id)

            if rooms:
                for room in rooms:
                    users_list_rooms.append(
                        f'Ваша комната: {room.name} ({room.number})'
                    )

    create_room = types.KeyboardButton(text="Создать комнату 🔨")
    join_room = types.KeyboardButton(text="Войти в комнату 🏠")
    about = types.KeyboardButton(text="Об игре ℹ️")
    user_profile = types.KeyboardButton(text="Мой профиль 👤")

    keyboard.add(join_room, create_room)
    if users_list_rooms:
        for room in users_list_rooms:
            keyboard.add(room)
    keyboard.add(user_profile)
    keyboard.add(about)

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
