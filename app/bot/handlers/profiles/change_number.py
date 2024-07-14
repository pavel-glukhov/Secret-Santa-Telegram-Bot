import logging
import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.profiles import ChangePhoneNuber
from app.config import load_config
from app.store.encryption import CryptData
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_number')
async def change_phone_number(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        'Укажите ваш номер телефона, что бы почтовые служащие '
        'смогли оповестить вас о прибывшем подарке.\n\n'
        '<b>Введите свой номер используя формат: +7|8(___)___-__-__ </b> \n'
        '<b>Например:</b> +7 700 111 11 11'
    )
    
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangePhoneNuber.waiting_for_phone_number)


@router.message(ChangePhoneNuber.waiting_for_phone_number)
async def process_changing_owner(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    phone_number = message.text
    user_id = message.chat.id
    
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    cancel_keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "profile_edit",
        }
    )
    
    pattern = r'(\+7|\+?7|8|\+?\d{3})\D*\d{3}[\s-]*\d{2}[\s-]*\d{2}|\+?\d{11}'
    if re.search(pattern, phone_number):
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=phone_number)
        await UserRepo().update_user(user_id, encrypted_number=encrypted_data)
        logger.info(f'The user [{user_id}] updated call number.')
        message_text = 'Номер изменен.'
        
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        await state.clear()
    else:
        
        message_text = (
            '<b>❌Неверный формат номера❌, попробуйте ещё раз.</b>\n\n'
            '<b>Укажи свой номер используя формат: +7|8(___)___-__-__ </b> \n'
            '<b>Например:</b> +7 700 111 11 11'
        )
        return await bot_message.edit_text(
            text=message_text,
            reply_markup=cancel_keyboard_inline,
        )