import aiogram.types
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ParseMode
from app import dispatcher as dp, bot
from aiogram import types


@dp.message_handler(lambda message: message.text == "Мой профиль 👤")
async def my_profile(message: types.Message):
    edit_user_profile = types.InlineKeyboardButton(
        text="👋 Изменить профиль",
        callback_data="profile_edit"
    )
    keyboard_inline = types.InlineKeyboardMarkup().add(edit_user_profile)
    await message.answer("Предоставленными вами данные необходимы для отправки"
                         " подарка вашим Тайным Сантой.\n\n"
                         "*Ваш профиль*:\n\n"
                         "Полное имя: \n"
                         "Адрес:\n"
                         "Номер телефона:\n"
                         "Email:\n"
                         "\n", parse_mode=ParseMode.MARKDOWN)
    await message.answer("Если вы желаете изменить личные данные,"
                         " или удалить их, нажмите на кнопку "
                         "'Изменить профиль'",
                         reply_markup=keyboard_inline)


async def edit_profile(message: types.Message):
    keyboard_inline = types.InlineKeyboardMarkup()
    edit_name = types.InlineKeyboardButton(
        text="Изменить имя",
        callback_data="profile_edit_name"
    )
    edit_address = types.InlineKeyboardButton(
        text="Изменить адрес",
        callback_data="profile_edit_address"
    )
    edit_number = types.InlineKeyboardButton(
        text="Изменить номер телефона",
        callback_data="profile_edit_number"
    )
    delete_all = types.InlineKeyboardButton(
        text="Удалить всю информацию ❌",
        callback_data="profile_edit_delete_all"
    )

    keyboard_inline.add(edit_name)
    keyboard_inline.add(edit_address)
    keyboard_inline.add(edit_number)
    keyboard_inline.add(delete_all)

    await message.edit_text("Выберите, что вы хотите изменить:",
                            reply_markup=keyboard_inline)
