import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message
from app.bot.handlers.profiles.states import DeleteUserInformation
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='profile_edit_delete_all'))
async def delete_user_information(callback: types.CallbackQuery):
    await DeleteUserInformation.waiting_for_conformation.set()
    state = dp.get_current().current_state()
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    message_text = (
        'Напиши <b>подтверждаю</b> для удаления твоих данных из профиля.\n\n'
    )
    
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteUserInformation.waiting_for_conformation)
async def process_deleting_information_invalid(message: types.Message):
    state = dp.get_current().current_state()
    state_data = await state.get_data()
    last_message = state_data['last_message']
    await delete_user_message(message.from_user.id, message.message_id)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    
    message_text = (
        'Вы ввели неверную команду. Попробуйте снова.\n\n'
        'Для подтверждения, введите слово <b>"подтверждаю"</b>'
    )
    return await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() == 'подтверждаю',
                    state=DeleteUserInformation.waiting_for_conformation)
async def process_deleting_information(message: types.Message,
                                       state: FSMContext):
    user_id = message.chat.id
    state_data = await state.get_data()
    last_message = state_data['last_message']
    await delete_user_message(message.from_user.id, message.message_id)
    
    data = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'encrypted_address': None,
        'encrypted_number': None,
    }
    await UserRepo().update_user(user_id=user_id, **data)
    logger.info(f'The user [{user_id}] deleted personal information.'
                )
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "menu_user_profile",
        }
    )
    
    message_text = 'Все данные о вас были удалены.\n\n'
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.finish()
