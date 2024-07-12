import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message, get_room_number
from app.bot.states.rooms import ChangeRoomName
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_change-name'))
async def update_room_name(callback: types.CallbackQuery):
    state = dp.get_current().current_state()
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    await ChangeRoomName.waiting_for_room_name.set()
    
    message_text = (
        'Введите новое имя для вашей комнаты.\n'
        'Имя не должно превышать 16 символов\n'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


@dp.message_handler(lambda message:
                    len(message.text.lower()) > 16,
                    state=ChangeRoomName.waiting_for_room_name)
async def process_change_room_name_invalid(message: types.Message):
    state_data = await dp.get_current().current_state().get_data()
    last_message = state_data['last_message']
    cancel_keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long room name'
                f' command from [{message.from_user.id}] ')
    
    await delete_user_message(message.from_user.id, message.message_id)
    
    message_text = (
        'Вы ввели слишком длинное имя, '
        'пожалуйста придумайте другое.\n'
        'Имя комнаты не должно превышать 16 символов.\n'
    )
    await last_message.edit_text(
        text=message_text,
        reply_markup=cancel_keyboard_inline,
    )


@dp.message_handler(state=ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    new_room_name = message.text
    last_message = state_data['last_message']
    
    await RoomRepo().update(room_number=room_number,
                            name=new_room_name)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_config_{room_number}",
        }
    )
    logger.info(f'The user[{message.from_user.id}] '
                f'changed name of the [{room_number}]')
    
    await delete_user_message(message.from_user.id, message.message_id)
    
    message_text = f'Имя комнаты  изменено на <b>{new_room_name}</b>'
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.finish()
