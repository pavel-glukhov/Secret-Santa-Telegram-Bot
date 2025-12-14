import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.rooms_states import ChangeOwner
from app.bot.utils import safe_delete_message
from app.core.config.app_config import load_config
from app.core.database.repo.rooms import RoomRepo
from app.core.database.repo.users import UserRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_change-owner'))
async def change_room_owner(callback: types.CallbackQuery,
                            state: FSMContext,
                            lang: TranslationMainSchema,
                            room_number: int):
    await state.update_data(room_number=room_number)

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})

    message_text = lang.messages.rooms_menu.change_owner.change_owner_room_first_msg

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeOwner.waiting_for_owner_name)


@router.message(ChangeOwner.waiting_for_owner_name)
async def process_changing_owner(message: types.Message,
                                 state: FSMContext,
                                 session: AsyncSession, lang: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    previous_owner = message.chat.id
    new_owner = message.text
    await safe_delete_message(message, log_prefix="process_changing_owner")
    bot_message = state_data['bot_message_id']
    return_back_button = lang.buttons.return_back_button

    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: f"room_menu_{room_number}",
        }
    )
    user = await UserRepo(session).get_user_or_none(new_owner)

    if not user:
        message_text = lang.messages.rooms_menu.change_owner.user_is_not_exist
    else:
        count_rooms = await RoomRepo(session).get_count_user_rooms(user.user_id)

        if count_rooms < load_config().room.user_rooms_count:
            await RoomRepo(session).change_owner(new_owner, room_number)
            message_text = lang.messages.rooms_menu.change_owner.change_owner_room_first_msg.format(
                new_owner=new_owner
            )
            logger.info(f'The owner [{previous_owner}] of room '
                        f'[{room_number}] has been changed to [{user.user_id}]')
        else:
            message_text = lang.messages.rooms_menu.change_owner.error

    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.clear()
