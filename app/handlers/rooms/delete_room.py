from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import keyboard_button


class DeleteRoom(StatesGroup):
    waiting_conformation = State()


async def delete_room(message: types.Message,
                      room_number: Union[int, str]):
    await DeleteRoom.waiting_conformation.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    keyboard_inline = keyboard_button(text="Отмена",
                                      callback='cancel')

    await message.edit_text(
        '❌ *Комната будет удалена без возможности восстановления*.\n\n'
        f'Для подтверждения удаления комнаты *{room_number}*, '
        f'введите в чат *подтверждаю*.\n\n '
        'Что бы отменить удаление, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteRoom.waiting_conformation)
async def process_delete_room_invalid(message: types.Message):
    return await message.reply(
        'Вы ввели неверную команду для подтверждения, попробуйте снова.\n'
        'Что бы отменить удаление, введите в чате *отмена*',
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(
    state=DeleteRoom.waiting_conformation)
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    data = await dp.current_state().get_data()
    room_number = data['room_number']
    keyboard_inline = keyboard_button(text="Вернуться назад ◀️",
                                      callback="root_menu")

    is_deleted = await room_db().delete(room_number=room_number)
    if is_deleted:
        await message.answer(
            'Комната успешно удалена\n\n'
            'Вы можете создать новую комнату в основном меню.',
            reply_markup=keyboard_inline
        )
    else:
        await message.answer(
            'Что-то пошло не так, комната не была удалена',
            reply_markup=keyboard_inline
        )
    await state.finish()
