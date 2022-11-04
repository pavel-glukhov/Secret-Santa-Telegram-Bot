from aiogram import types

from app.bot import dispatcher as dp
from app.bot.handlers.rooms.create_new_room import CreateRoom

from app.bot.handlers.rooms.update_room import ChangeRoomName
from app.bot.keyborads.common import generate_inline_keyboard


@dp.message_handler(lambda message: len(message.text) > 12,
                    state=ChangeRoomName.waiting_for_room_name)
@dp.message_handler(lambda message: len(message.text) > 12,
                    state=CreateRoom.waiting_for_room_name)
async def room_name_invalid(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    return await message.answer(
        text='Вы ввели слишком длинное имя, '
             'пожалуйста придумайте другое.\n'
             'Имя комнаты не должно превышать 12 символов.\n',
        reply_markup=keyboard_inline
    )
