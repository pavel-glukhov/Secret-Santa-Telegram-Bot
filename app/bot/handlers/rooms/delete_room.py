import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers import texts
from app.store.database import room_db
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.handlers.operations import get_room_number

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
    
    await callback.message.edit_text(
        texts.DELETE_ROOM_MAIN_QUESTION.format(room_number, ),
        reply_markup=keyboard_inline
    )


@dp.message_handler(lambda message:
                    message.text.lower() != texts.DELETE_CONFIRMATION_COMMAND,
                    state=DeleteRoom.waiting_conformation)
async def process_delete_room_invalid(message: types.Message):
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    logger.info('Incorrect confirmation'
                f' command from [{message.from_user.id}] ')
    return await message.answer(
        texts.DELETE_ROOM_INCORRECT_CONF_COMMAND,
        reply_markup=keyboard_inline
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
    
    is_deleted = await room_db().delete(room_number=room_number)
    if is_deleted:
        await message.answer(
            texts.DELETE_ROOM_SUCCEFUL,
            reply_markup=keyboard_inline
        )
        logger.info(f'The user [{message.from_user.id}]'
                    f' removed the room [{room_number}]')
    else:
        await message.answer(
            texts.DELETE_ROOM_SOMETHING_WRONG,
            reply_markup=keyboard_inline
        )
        logger.info(f'The room [{room_number}]'
                    'was not removed removed'
                    f' by[{message.from_user.id}] ')
    await state.finish()
