import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number, delete_user_message
from app.bot.handlers.rooms.states import ChangeRoomName
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_change-name'))
async def update_room_name(callback: types.CallbackQuery):
    state_data = await dp.get_current().current_state().get_data()
    room_number = get_room_number(callback)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})

    await ChangeRoomName.waiting_for_room_name.set()
    state_data.update(room_number=room_number)
    message_text = (
        'Введите новое имя для вашей комнаты.\n'
        'Имя не должно превышать 12 символов\n'
    )
    state_data['last_message'] = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )

@dp.message_handler(state=ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    new_room_name = message.text

    if not len(new_room_name) < 13:
        await delete_user_message(message.from_user.id, message.message_id)
        cancel_keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
        await state_data['last_message'].edit_text(
            text='Вы ввели слишком длинное имя, '
                 'пожалуйста придумайте другое.\n'
                 'Имя комнаты не должно превышать 12 символов.\n',
            reply_markup=cancel_keyboard_inline
        )
        
    await RoomDB.update(room_number=room_number,
                        name=new_room_name)

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    logger.info(
        f'The user[{message.from_user.id}] changed name of the [{room_number}]'
    )
    await delete_user_message(message.from_user.id, message.message_id)
    last_message = state_data['last_message']
    message_text = f'Имя комнаты  изменено на <b>{new_room_name}</b>'
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.finish()
