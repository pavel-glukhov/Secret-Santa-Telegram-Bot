import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.operations import delete_user_message, get_room_number
from app.bot.handlers.rooms.states import DeleteRoom
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_delete'))
async def delete_room(callback: types.CallbackQuery):
    state = dp.get_current().current_state()
    room_number = get_room_number(callback)
    await DeleteRoom.waiting_conformation.set()
    await state.update_data(room_number=room_number)
    await state.update_data(question_message_id=callback.message.message_id)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        '❌<b>Комната будет удалена без'
        ' возможности восстановления</b>.\n\n'
        f'Для подтверждения удаления комнаты <b>{room_number}</b>, '
        'введите в чат <b>подтверждаю</b>.\n\n '
    )
    
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


@dp.message_handler(lambda message:
                    message.text.lower() != 'подтверждаю',
                    state=DeleteRoom.waiting_conformation)
async def process_delete_room_invalid(message: types.Message):
    state_data = await dp.get_current().current_state().get_data()
    last_message = state_data['last_message']
    room_number = state_data['room_number']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('Incorrect confirmation'
                f' command from [{message.from_user.id}] ')
        
    await delete_user_message(message.from_user.id, message.message_id)

    message_text = (
        f'Вы ввели неверную команду "'
        f'<b>{message.text}</b>" для подтверждения.\n\n'
        f'Для подтверждения удаления комнаты <b>{room_number}</b>, '
        'введите в чат <b>подтверждаю</b>.\n\n '
    )
    await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )


@dp.message_handler(
    state=DeleteRoom.waiting_conformation)
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    state_data = await state.get_data()
    last_message = state_data['last_message']
    room_number = state_data['room_number']
    await delete_user_message(message.from_user.id, message.message_id)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )

    is_room_deleted = await RoomDB.delete(room_number=room_number)
    
    if is_room_deleted:
        message_text = (
            'Комната успешно удалена\n\n '
            'Вы можете создать новую комнату в основном меню.'
        )
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )

        logger.info(
            f'The user [{message.from_user.id}]'
            f' removed the room [{room_number}]'
        )
    else:
        message_text = 'Что-то пошло не так, комната не была удалена'
        
        await last_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(
            f'The room [{room_number}]'
                    'was not removed removed'
                    f' by[{message.from_user.id}] '
        )
    
    await state.finish()