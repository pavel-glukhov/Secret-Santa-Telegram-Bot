import logging
import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.profiles_states import ChangePhoneNuber
from app.bot.utils import safe_delete_message
from app.core.config.app_config import load_config
from app.core.database.repo.users import UserRepo
from app.core.encryption import CryptData

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_number')
async def change_phone_number(callback: types.CallbackQuery,
                              state: FSMContext,
                              lang: TranslationMainSchema):
    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    message_text = lang.messages.profile_menu.change_number.change_number_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangePhoneNuber.waiting_for_phone_number)


@router.message(ChangePhoneNuber.waiting_for_phone_number)
async def process_changing_owner(message: types.Message,
                                 state: FSMContext,
                                 session: AsyncSession,
                                 lang: TranslationMainSchema):
    state_data = await state.get_data()
    phone_number = message.text
    user_id = message.chat.id
    bot_message = state_data['bot_message_id']

    await safe_delete_message(message, log_prefix="process_changing_owner")

    cancel_button = lang.buttons.cancel_button
    cancel_keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: "profile_edit",
        }
    )

    pattern = r'(\+7|\+?7|8|\+?\d{3})\D*\d{3}[\s-]*\d{2}[\s-]*\d{2}|\+?\d{11}'
    if re.search(pattern, phone_number):
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=phone_number)
        await UserRepo(session).update_user(user_id, encrypted_number=encrypted_data)
        logger.info(f'The user [{user_id}] updated call number.')

        message_text = lang.messages.profile_menu.change_number.change_number_second_msg

        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
        await state.clear()
    else:
        message_text = lang.messages.profile_menu.change_number.error
        return await bot_message.edit_text(text=message_text, reply_markup=cancel_keyboard_inline)
