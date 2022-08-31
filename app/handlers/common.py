from aiogram import types
from aiogram.dispatcher import FSMContext

from app.database import room_db, user_db
from app.keyborads.common import create_common_keyboards


async def cancel_handler(message: types.Message):
    keyboard = await create_common_keyboards(message)

    await message.answer("Действие отменено",
                         reply_markup=keyboard)


async def start(message: types.Message):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name

    await user_db().create_user_or_get(username=username,
                                       user_id=user_id,
                                       first_name=first_name,
                                       last_name=last_name)

    keyboard = await create_common_keyboards(message)
    await room_db().get_joined_in_rooms(user_id)
    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
        reply_markup=keyboard
    )


async def about_game(message: types.Message):
    msg = 'Это адаптированная игра "Тайный Санта"'
    await message.answer(msg)
