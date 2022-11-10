import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


class DeleteRoom(StatesGroup):
    waiting_conformation = State()


@dp.callback_query_handler(Text(startswith='room_delete'))
async def delete_room(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await DeleteRoom.waiting_conformation.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    message_text = (
        '❌<b>Комната будет удалена без'
        ' возможности восстановления</b>.\n\n'
        f'Для подтверждения удаления комнаты <b>{room_number}</b>, '
        'введите в чат <b>подтверждаю</b>.\n\n '
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteRoom.waiting_conformation)
async def process_delete_room_invalid(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    logger.info('Incorrect confirmation'
                f' command from [{message.from_user.id}] ')
    
    message_text = (
        'Вы ввели неверную команду для подтверждения,'
        ' попробуйте снова.\n'
    )
    return await message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(
    state=DeleteRoom.waiting_conformation)
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    
    is_deleted = await RoomDB.delete(room_number=room_number)
    if is_deleted:
        
        message_text = (
            'Комната успешно удалена\n\n '
            'Вы можете создать новую комнату в основном меню.'
        )
        
        await message.answer(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(f'The user [{message.from_user.id}]'
                    f' removed the room [{room_number}]')
    else:
        message_text = 'Что-то пошло не так, комната не была удалена'
        
        await message.answer(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(f'The room [{room_number}]'
                    'was not removed removed'
                    f' by[{message.from_user.id}] ')
    await state.finish()
