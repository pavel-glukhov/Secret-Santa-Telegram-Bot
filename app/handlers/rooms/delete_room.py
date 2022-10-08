import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import dispatcher as dp
from app.database import room_db
from app.keyborads.common import generate_inline_keyboard

logger = logging.getLogger(__name__)


class DeleteRoom(StatesGroup):
    waiting_conformation = State()


# TODO добавить логирование
@dp.callback_query_handler(Text(startswith='room_delete'))
async def delete_room(callback: types.CallbackQuery):
    command, operation, room_number = callback.data.split('_')
    message = callback.message
    await DeleteRoom.waiting_conformation.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    await message.edit_text(
        '❌ *Комната будет удалена без возможности восстановления*.\n\n'
        f'Для подтверждения удаления комнаты *{room_number}*, '
        f'введите в чат *подтверждаю*.\n\n '
        'Что бы отменить удаление, введите в чате *отмена*',
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteRoom.waiting_conformation)
async def process_delete_room_invalid(message: types.Message):
    return await message.reply(
        'Вы ввели неверную команду для подтверждения, попробуйте снова.\n'
        'Что бы отменить удаление, введите в чате *отмена*',
    )


@dp.message_handler(
    state=DeleteRoom.waiting_conformation)
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    data = await dp.current_state().get_data()
    room_number = data['room_number']
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )

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
