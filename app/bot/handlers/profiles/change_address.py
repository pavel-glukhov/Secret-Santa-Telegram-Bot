import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.states.profiles import ChangeAddress
from app.config import load_config
from app.store.database.queries.users import UserRepo
from app.store.encryption import CryptData

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'profile_edit_address')
async def change_user_address(callback: types.CallbackQuery,
                              state: FSMContext,
                              app_text_msg: TranslationMainSchema):
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'}
    )
    
    message_text = app_text_msg.messages.profile_menu.change_address.change_address_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeAddress.waiting_for_address_information)


@router.message(ChangeAddress.waiting_for_address_information)
async def process_changing_owner(message: types.Message,
                                 state: FSMContext,
                                 session: Session,
                                 app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    address = message.text
    user_id = message.chat.id
    
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: "profile_edit",
        }
    )
    
    if len(address) < 150:
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=address)
        await UserRepo(session).update_user(user_id, encrypted_address=encrypted_data)
        logger.info(f'The user [{user_id}] updated an address.')
        
        message_text = app_text_msg.messages.profile_menu.change_address.change_address_second_msg
        
        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
        await state.clear()
    else:
        message_text = app_text_msg.messages.profile_menu.change_address.error
    
        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
