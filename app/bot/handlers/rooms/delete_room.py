import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.bot.handlers.operations import get_room_number
from app.bot.states.rooms import DeleteRoom
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_delete'))
async def delete_room(callback: types.CallbackQuery, state: FSMContext):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    await state.update_data(question_message_id=callback.message.message_id)
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    
    message_text = (
        '❌<b>Комната будет удалена без'
        ' возможности восстановления</b>.\n\n'
        f'Для подтверждения удаления комнаты <b>{room_number}</b>, '
        'введите в чат <b>подтверждаю</b>.\n\n '
    )
    
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(DeleteRoom.waiting_conformation)


@router.message(lambda message: message.text.lower() not in ['подтверждаю', 'confirm'],
                StateFilter(DeleteRoom.waiting_conformation))
async def process_delete_room_invalid(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    keyboard_inline = generate_inline_keyboard({"Отмена": 'cancel'})
    logger.info('Incorrect confirmation'
                f' command from [{message.from_user.id}] ')
    await message.delete()
    bot_message = state_data['bot_message_id']
    message_text = (
        f'Вы ввели неверную команду "'
        f'<b>{message.text}</b>" для подтверждения.\n\n'
        f'Для подтверждения удаления комнаты <b>{room_number}</b>, '
        'введите в чат <b>подтверждаю</b>.\n\n '
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@router.message(lambda message: message.text.lower() in ['подтверждаю', 'confirm'],
                StateFilter(DeleteRoom.waiting_conformation))
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext):
    state_data = await state.get_data()
    await message.delete()
    
    bot_message = state_data['bot_message_id']
    room_number = state_data['room_number']
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    is_room_deleted = await RoomRepo().delete(room_number=room_number)
    
    if is_room_deleted:
        message_text = (
            'Комната успешно удалена\n\n '
            'Вы можете создать новую комнату в основном меню.'
        )
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        
        logger.info(
            f'The user [{message.from_user.id}]'
            f' removed the room [{room_number}]'
        )
    else:
        message_text = 'Что-то пошло не так, комната не была удалена'
        
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline,
        )
        logger.info(
            f'The room [{room_number}]'
            'was not removed removed'
            f' by[{message.from_user.id}] '
        )
    
    await state.clear()
