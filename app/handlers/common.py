from app import dispatcher as dp, bot
from aiogram import types
from app.database.operations import UserDB, RoomDB
from app.database.config import async_session
import logging


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    create_room = types.KeyboardButton(text="Создать комнату 🔨")
    join_room = "Войти в комнату 🏠"
    about_game = "Об игре ℹ️"
    user_profile = "Мой профиль 👤"

    keyboard.add(join_room, create_room)
    keyboard.add(user_profile)
    keyboard.add(about_game)

    async with async_session() as db_session:
        async with db_session.begin():
            user_db = UserDB(db_session)
            telegram_user = await user_db.get_user(telegram_id=user_id)
            if not telegram_user:
                logging.info(f'INFO: create new user: {user_id}')
                await user_db.create_user(
                    username=message.chat.username, telegram_id=message.chat.id
                )

    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
        reply_markup=keyboard
    )
