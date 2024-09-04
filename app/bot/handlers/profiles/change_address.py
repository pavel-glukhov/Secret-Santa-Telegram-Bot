import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.profiles import ChangeAddress
from app.config import load_config
from app.store.database.queries.users import UserRepo
from app.store.encryption import CryptData

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'profile_edit_address')
async def change_user_address(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    
    message_text = (
        'Для того, что бы ваш Тайный Санта смог отправить вам посылку, '
        'напишите ваш адрес куда необходимо отправить посылку'
        ' и не забудьте указать:\n\n'
        '<b>— Страну</b>\n'
        '<b>— область</b>\n'
        '<b>— город</b>\n'
        '<b>— улицу</b>\n'
        '<b>— дом</b>\n'
        '<b>— квартиру</b>\n'
        '<b>— этаж</b>*\n'
        '<b>— номер на домофоне, если отличается от квартиры</b>\n'
        '<b>— индекс</b>\n\n'
        '<b>Например: Россия, Московская область, г. Фрязино, ул. Пупкина,'
        ' д. 99, кв. 999, этаж 25, индекс 123987.</b>\n'
    )
    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeAddress.waiting_for_address_information)


@router.message(ChangeAddress.waiting_for_address_information)
async def process_changing_owner(message: types.Message, state: FSMContext, session: Session):
    state_data = await state.get_data()
    address = message.text
    user_id = message.chat.id
    
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "profile_edit",
        }
    )
    
    if len(address) < 150:
        crypt = CryptData(key=load_config().encryption.key)
        encrypted_data = crypt.encrypt(data=address)
        await UserRepo(session).update_user(user_id, encrypted_address=encrypted_data)
        logger.info(f'The user [{user_id}] updated an address.')
        
        message_text = 'Адрес изменен.'
        
        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
        await state.clear()
    else:
        message_text = (
            'Адресные данные не могут превышать 150 символов.'
            ' Попробуйте снова.'
        )
        await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
