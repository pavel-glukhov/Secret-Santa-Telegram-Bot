from aiogram import types
from aiogram.types import ParseMode


async def room_name_invalid(message: types.Message):
    return await message.reply(
        text='Вы ввели слишком длинное имя, '
             'пожалуйста придумайте другое.\n'
             'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN, )

# TODO добавить выбор пожелания
async def process_join_room_invalid_text_type(message: types.Message):
    return await message.reply(
        text='Номер комнаты может содержать только цифры, '
             'попробуйте снова.\n'
             'Что бы отменить процесс, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN, )
