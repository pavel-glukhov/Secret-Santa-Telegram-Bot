from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import create_common_keyboards


class ChangeRoomName(StatesGroup):
    waiting_for_room_name = State()


async def update_room_name(message: types.Message,
                           room_number: Union[str, int]):
    await ChangeRoomName.waiting_for_room_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    await message.edit_text(f'Введите новое имя для вашей комнаты.\n'
                            f'Имя не должно превышать 12 символов\n'
                            'Что бы отменить процесс, введите в чате *отмена*',
                            parse_mode=ParseMode.MARKDOWN)


async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    new_room_name = message.text
    async with state.proxy() as data:
        await room_db().update_room(room_number=data['room_number'],
                                    name=new_room_name)

    keyboard = await create_common_keyboards(message)
    await state.finish()
    await message.answer(
        f'Имя комнаты  изменено на *{new_room_name}*',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
