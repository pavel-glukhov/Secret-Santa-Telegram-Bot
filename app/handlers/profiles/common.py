import logging

from aiogram import types

from app.database import user_db
from app.keyborads.common import generate_inline_keyboard
from app.utils.formatters import user_information_formatter

logger = logging.getLogger(__name__)


async def my_profile(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить профиль 👋": "profile_edit",
            "Вернуться назад ◀️": "root_menu",
        }
    )

    user_id = message.chat.id
    user = await user_db().get_user_or_none(user_id)
    user_information = user_information_formatter(user)

    await message.edit_text(
        'Предоставленные вами данные необходимы для отправки'
        ' подарка вашим Тайным Сантой.\n\n'
        '*Ваш профиль*:\n\n'
        f'{user_information}\n\n,'
        'Если вы желаете изменить личные данные,'
        ' или удалить их, нажмите на кнопку '
        '*Изменить профиль*',
        reply_markup=keyboard_inline
    )


async def edit_profile(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {"Изменить имя": "profile_edit_name",
         "Изменить адрес": "profile_edit_address",
         "Изменить номер телефона": "profile_edit_number",
         "Удалить всю информацию ❌": "profile_edit_delete_all",
         "Вернуться назад ◀️": "menu_user_profile"

         }
    )
    await message.edit_text("Выберите, что вы хотите изменить:",
                            reply_markup=keyboard_inline)
