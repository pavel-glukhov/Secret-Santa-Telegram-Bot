import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.rooms_states import ChangeRoomName
from app.bot.utils import safe_delete_message
from app.core.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-name'))
async def update_room_name(callback: types.CallbackQuery,
                           state: FSMContext,
                           lang: TranslationMainSchema,
                           room_number: int):
    await state.update_data(room_number=room_number)

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})

    message_text = lang.messages.rooms_menu.update_room.update_room_first_msg

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeRoomName.waiting_for_room_name)


@router.message(lambda message: len(message.text.lower()) > 16,
                StateFilter(ChangeRoomName.waiting_for_room_name))
async def process_change_room_name_invalid(message: types.Message,
                                           state: FSMContext,
                                           lang: TranslationMainSchema):
    state_data = await state.get_data()
    await safe_delete_message(message, log_prefix="process_change_room_name_invalid")
    bot_message = state_data['bot_message_id']

    cancel_button = lang.buttons.cancel_button
    cancel_keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    logger.info('long room name'
                f' command from [{message.from_user.id}] ')

    message_text = lang.messages.rooms_menu.update_room.long_name
    await bot_message.edit_text(
        text=message_text,
        reply_markup=cancel_keyboard_inline
    )


@router.message(ChangeRoomName.waiting_for_room_name)
async def update_room_name_get_value(message: types.Message,
                                     state: FSMContext,
                                     session: AsyncSession,
                                     lang: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    new_room_name = message.text
    await safe_delete_message(message, log_prefix="update_room_name_get_value")

    bot_message = state_data['bot_message_id']

    await RoomRepo(session).update(
        room_number=room_number,
        name=new_room_name
    )

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: f"room_config_{room_number}",
        }
    )
    logger.info(f'The user[{message.from_user.id}] '
                f'changed name of the [{room_number}]')

    message_text = lang.messages.rooms_menu.update_room.update_room_second_msg.format(
        new_room_name=new_room_name
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.clear()
