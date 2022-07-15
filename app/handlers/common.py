from aiogram.dispatcher.filters import Text

from app import dispatcher as dp, bot
from aiogram import types
from app.database.operations import UserDB
from app.database.config import async_session
import logging


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    create_room = types.KeyboardButton(text="Создать комнату 🔨")
    join_room = types.KeyboardButton(text="Войти в комнату 🏠")
    about_game = types.KeyboardButton(text="Об игре ℹ️")
    user_profile = types.KeyboardButton(text="Мой профиль 👤")

    keyboard.add(join_room, create_room)
    keyboard.add(user_profile)
    keyboard.add(about_game)

    async with async_session() as db_session:
        async with db_session.begin():
            user_db = UserDB(db_session)
            telegram_user = await user_db.get_user(user_id=user_id)
            if not telegram_user:
                logging.info(f'INFO: create new user: {user_id}')
                await user_db.create_user(
                    username=message.chat.username,
                    user_id=message.chat.id,
                    first_name=message.chat.first_name,
                    last_name=message.chat.last_name
                )

    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
        reply_markup=keyboard
    )
