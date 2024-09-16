import logging
import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.states.profiles import ChangePhoneNuber
from app.config import load_config
from app.store.database.queries.users import UserRepo
from app.store.encryption import CryptData

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_number')
async def change_phone_number(callback: types.CallbackQuery,
                              state: FSMContext,
                              app_text_msg: TranslationMainSchema):
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'}
    )
    
    message_text = app_text_msg.messages.profile_menu.change_number.change_number_first_msg
   
    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangePhoneNuber.waiting_for_phone_number)


@router.message(ChangePhoneNuber.waiting_for_phone_number)
async def process_changing_owner(message: types.Message,
                                 state: FSMContext,
                                 session: Session,
                                 app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    phone_number = message.text
    user_id = message.chat.id
    text = message.text
    bot_message = state_data['bot_message_id']
    
    await message.delete()
    
    cancel_keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'}
    )
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: "profile_edit",
        }
    )
    
    pattern = r'(\+7|\+?7|8|\+?\d{3})\D*\d{3}[\s-]*\d{2}[\s-]*\d{2}|\+?\d{11}'
    if re.search(pattern, phone_number):
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=phone_number)
        await UserRepo(session).update_user(user_id, encrypted_number=encrypted_data)
        logger.info(f'The user [{user_id}] updated call number.')

        message_text = app_text_msg.messages.profile_menu.change_number.change_number_second_msg

        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
        await state.clear()
    else:
        message_text = app_text_msg.messages.profile_menu.change_number.error
        return await bot_message.edit_text(text=message_text, reply_markup=cancel_keyboard_inline)
