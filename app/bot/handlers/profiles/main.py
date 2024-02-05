import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.formatters import profile_information_formatter
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.users import UserRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(equals='menu_user_profile'))
async def my_profile(callback: types.CallbackQuery):
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить профиль 👋": "profile_edit",
            "Вернуться назад ◀️": "root_menu",
        }
    )
    user = await UserRepo().get_user_or_none(message.chat.id)
    user_information = profile_information_formatter(user)
    
    message_text = (
        'Предоставленные вами данные необходимы для отправки'
        ' подарка вашим Тайным Сантой.\n\n'
        '<b>Ваш профиль</b>:\n\n'
        f'{user_information}\n\n'
        'Для обеспечения безопасности, '
        'мы шифруем адрес и номер телефона в базе.\n\n'
        'Если вы желаете изменить личные данные,'
        ' или удалить их, нажмите на кнопку '
        '<b>Изменить профиль</b>\n\n'
    )
    
    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(Text(equals='profile_edit'))
async def edit_profile(callback: types.CallbackQuery, ):
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            "Изменить имя": "profile_edit_name",
            "Изменить адрес": "profile_edit_address",
            "Изменить номер телефона": "profile_edit_number",
            "Изменить часовой пояс": "change_time_zone",
            "Удалить всю информацию ❌": "profile_edit_delete_all",
            "Вернуться назад ◀️": "menu_user_profile"
        }
    )
    
    message_text = "Выберите, что вы хотите изменить:"
    
    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
