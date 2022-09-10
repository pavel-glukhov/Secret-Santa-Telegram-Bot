import logging

from aiogram import types
from aiogram.types.message import ParseMode

from app.database import user_db
from app.utils.formatters import user_information_formatter

logger = logging.getLogger(__name__)


async def my_profile(message: types.Message):
    keyboard_inline = types.InlineKeyboardMarkup()

    keyboards = [
        types.InlineKeyboardButton(
            text="Изменить профиль 👋",
            callback_data="profile_edit"
        ),
        types.InlineKeyboardButton(
            text="Вернуться назад ◀️",
            callback_data="root_menu"
        )
    ]

    for button in keyboards:
        keyboard_inline.add(button)

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
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


async def edit_profile(message: types.Message):
    keyboard_inline = types.InlineKeyboardMarkup()

    keyboard_list = [
        types.InlineKeyboardButton(
            text="Изменить имя",
            callback_data="profile_edit_name"
        ),
        types.InlineKeyboardButton(
            text="Изменить адрес",
            callback_data="profile_edit_address"
        ),
        types.InlineKeyboardButton(
            text="Изменить номер телефона",
            callback_data="profile_edit_number"
        ),
        types.InlineKeyboardButton(
            text="Удалить всю информацию ❌",
            callback_data="profile_edit_delete_all"
        ),
        types.InlineKeyboardButton(
            text="Вернуться назад ◀️",
            callback_data="menu_user_profile"
        ),
    ]

    for button in keyboard_list:
        keyboard_inline.add(button)

    await message.edit_text("Выберите, что вы хотите изменить:",
                            reply_markup=keyboard_inline)
