import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.bot.handlers.operations import get_room_number
from app.bot.states.rooms import ChangeRoomName
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-name'))
async def update_room_name(callback: types.CallbackQuery, state: FSMContext):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Введите новое имя для вашей комнаты.\n'
        'Имя не должно превышать 16 символов\n'
    )
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeRoomName.waiting_for_room_name)


@router.message(lambda message: len(message.text.lower()) > 16,
                StateFilter(ChangeRoomName.waiting_for_room_name))
async def process_change_room_name_invalid(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    cancel_keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('long room name'
                f' command from [{message.from_user.id}] ')
    
    message_text = (
        'Вы ввели слишком длинное имя, '
        'пожалуйста придумайте другое.\n'
        'Имя комнаты не должно превышать 16 символов.\n'
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=cancel_keyboard_inline,
    )


@router.message(ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    new_room_name = message.text
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    
    await RoomRepo().update(room_number=room_number,
                            name=new_room_name)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_config_{room_number}",
        }
    )
    logger.info(f'The user[{message.from_user.id}] '
                f'changed name of the [{room_number}]')
    
    message_text = f'Имя комнаты  изменено на <b>{new_room_name}</b>'
    
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.clear()
