import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.profiles import DeleteUserInformation
from app.store.database.queries.users import UserRepo

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'profile_edit_delete_all')
async def delete_user_information(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    message_text = (
        'Напиши <b>подтверждаю</b> для удаления твоих данных из профиля.\n\n'
    )
    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(DeleteUserInformation.waiting_for_conformation)


@router.message(lambda message: message.text.lower() not in ['подтверждаю', 'confirm'],
                StateFilter(DeleteUserInformation.waiting_for_conformation))
async def process_deleting_information_invalid(message: types.Message, state: FSMContext):
    command = message.text
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel', }
    )
    
    message_text = (
        f'Вы ввели неверную "{command}" команду. Попробуйте снова.\n\n'
        'Для подтверждения, введите слово <b>"подтверждаю"</b>'
    )
    return await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(lambda message: message.text.lower() in ['подтверждаю', 'confirm'],
                StateFilter(DeleteUserInformation.waiting_for_conformation))
async def process_deleting_information(message: types.Message,
                                       state: FSMContext, session: Session):
    user_id = message.chat.id
    state_data = await state.get_data()
    
    await message.delete()
    bot_message = state_data['bot_message_id']
    data = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'encrypted_address': None,
        'encrypted_number': None,
    }
    await UserRepo(session).update_user(user_id=user_id, **data)
    logger.info(f'The user [{user_id}] deleted personal information.'
                )
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    
    message_text = 'Все данные о вас были удалены.\n\n'
    
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.clear()
