from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import create_common_keyboards


class DeleteRoom(StatesGroup):
    waiting_conformation = State()


async def delete_room(message: types.Message,
                      room_number: Union[int, str]):
    await DeleteRoom.waiting_conformation.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    await message.edit_text(
        '*Комната будет удалена без возможности восстановления*.\n\n'
        f'Для подтверждения удаления комнаты *{room_number}*, '
        f'введите в чат *подтверждаю*.\n\n '
        'Что бы отменить удаление, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


async def process_delete_room_invalid(message: types.Message):
    return await message.reply(
        'Вы ввели неверную команду для подтверждения, попробуйте снова.\n'
        'Что бы отменить удаление, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN, )


async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    async with state.proxy() as data:
        await room_db().delete(room_number=data['room_number'])

    keyboard = await create_common_keyboards(message)

    await message.answer(
        'Комната успешно удалена\n\n'
        'Вы можете создать новую комнату в меню ниже.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
    await state.finish()
