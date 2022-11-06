import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.store.database import room_db
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.handlers.operations import get_room_number

logger = logging.getLogger(__name__)


class ChangeRoomName(StatesGroup):
    waiting_for_room_name = State()


@dp.callback_query_handler(Text(startswith='room_change-name'))
async def update_room_name(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    await ChangeRoomName.waiting_for_room_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    await callback.message.edit_text(f'Введите новое имя для вашей комнаты.\n'
                                     f'Имя не должно превышать 12 символов\n',
                                     reply_markup=keyboard_inline
                                     )


@dp.message_handler(state=ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']

    new_room_name = message.text
    await room_db().update(room_number=room_number,
                           name=new_room_name)

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    logger.info(f'The user[{message.from_user.id}] changed name of the [{room_number}]')
    await state.finish()
    await message.answer(
        f'Имя комнаты  изменено на <b>{new_room_name}</b>',
        reply_markup=keyboard_inline
    )