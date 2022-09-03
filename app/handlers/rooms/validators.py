from aiogram import types
from aiogram.types import ParseMode
from app import dispatcher as dp
from app.handlers.rooms.create_room import CreateRoom
from app.handlers.rooms.subscribe_room import JoinRoom
from app.handlers.rooms.update_room import ChangeRoomName
from app.keyborads.common import keyboard_button


@dp.message_handler(lambda message: len(message.text) > 12,
                    state=ChangeRoomName.waiting_for_room_name)
@dp.message_handler(lambda message: len(message.text) > 12,
                    state=CreateRoom.waiting_for_room_name)
async def room_name_invalid(message: types.Message):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    return await message.reply(
        text='Вы ввели слишком длинное имя, '
             'пожалуйста придумайте другое.\n'
             'Имя комнаты не должно превышать 12 символов.\n',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=JoinRoom.waiting_for_room_number)
async def process_join_room_invalid_text_type(message: types.Message):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')
    return await message.reply(
        text='Номер комнаты может содержать только цифры, '
             'попробуйте снова.\n'
             'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )
