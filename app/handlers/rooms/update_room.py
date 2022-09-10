import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import keyboard_button

logger = logging.getLogger(__name__)


class ChangeRoomName(StatesGroup):
    waiting_for_room_name = State()


async def update_room_name(message: types.Message,
                           room_number: Union[str, int]):
    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')

    await ChangeRoomName.waiting_for_room_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    await message.edit_text(f'Введите новое имя для вашей комнаты.\n'
                            f'Имя не должно превышать 12 символов\n',
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=keyboard_inline
                            )

# TODO добавить логирование
@dp.message_handler(state=ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    data = await dp.current_state().get_data()
    room_number = data['room_number']

    new_room_name = message.text
    await room_db().update_room(room_number=room_number,
                                name=new_room_name)

    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback="root_menu")
    await state.finish()
    await message.answer(
        f'Имя комнаты  изменено на *{new_room_name}*',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )
