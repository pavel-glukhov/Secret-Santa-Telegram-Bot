from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dispatcher as dp
from app.database import room_db, user_db
from app.keyborads.common import create_common_keyboards


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Хо-хо-хо! 🎅\n\n"
        "Вот и настало поиграть в Тайного Санту!\n\n"
        "Создай свою комнату для друзей, или подключись к существующей.",
    )
    await root_menu(message)


@dp.message_handler(commands=['menu'])
async def root_menu(message: types.Message, edit_previous_message=False):
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name

    await user_db().create_user_or_get(username=username,
                                       user_id=user_id,
                                       first_name=first_name,
                                       last_name=last_name)

    keyboard = await create_common_keyboards(message)
    await room_db().get_all_user_rooms(user_id)
    if edit_previous_message:
        await message.edit_text("Меню", reply_markup=keyboard)
    else:
        await message.answer("Меню", reply_markup=keyboard)


@dp.message_handler(commands=['about'])
async def about_game(message: types.Message):
    msg = 'Это адаптированная игра "Тайный Санта"'
    await message.answer(msg)
