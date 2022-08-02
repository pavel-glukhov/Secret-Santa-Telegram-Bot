from aiogram import types
from aiogram.types import ParseMode


async def room_name_invalid(message: types.Message):
    return await message.reply(
        text='Вы ввели слишком длинное имя, '
             'пожалуйста придумайте другое.\n'
             'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN, )
