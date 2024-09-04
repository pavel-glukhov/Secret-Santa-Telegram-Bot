import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.bot.states.rooms import JoinRoom
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.wishes import WishRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_join_room')
async def join_room(callback: types.CallbackQuery, state: FSMContext):
    keyboard_inline = generate_inline_keyboard(
        {"Отмена": 'cancel'}
    )
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        'Введи номер комнаты в которую ты хочешь зайти.\n'
    )
    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(JoinRoom.waiting_for_room_number)


@router.message(JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message, state: FSMContext, session: Session):
    room_number = message.text
    state_data = await state.get_data()
    await state.update_data(room_number=room_number)
    bot_message_id = state_data.get('bot_message_id')
    await message.delete()
    if not room_number.isdigit():
        return await _edit_bot_message(
            bot_message_id,
            'Номер комнаты может содержать только цифры, попробуйте снова.',
            {"Отмена": 'cancel'}
        )
    
    room = await RoomRepo(session).get(room_number=int(room_number))
    
    if not room or room.is_closed:
        return await _is_not_exists_room(bot_message_id, room_number, {"Отмена": 'cancel'})
    
    is_member_of_room = await RoomRepo(session).is_member(user_id=message.chat.id,
                                                          room_number=int(room_number))
    
    if is_member_of_room:
        await _handle_existing_member(bot_message_id, message, state, session, room_number)
    else:
        await _request_wishes(bot_message_id, state)


async def _edit_bot_message(bot_message_id, text, buttons):
    keyboard_inline = generate_inline_keyboard(buttons)
    await bot_message_id.edit_text(text=text, reply_markup=keyboard_inline)


async def _handle_existing_member(bot_message_id, message, state, session, room_number):
    keyboard_inline = await create_common_keyboards(message, session)
    
    await _edit_bot_message(
        bot_message_id,
        'Вы уже состоите в этой комнате.',
        keyboard_inline
    )
    
    logger.info(f'The user[{message.from_user.id}] already is a member of the room [{room_number}]')
    await state.clear()


async def _request_wishes(bot_message_id, state):
    await state.set_state(JoinRoom.waiting_for_wishes)
    
    message_text = (
        'А теперь напишите свои пожелания к подарку. '
        'Возможно, у вас есть хобби и вы хотите получить что-то особенное?\n'
        'Ваши комментарии помогут Тайному Санте выбрать для вас подарок.\n'
    )
    
    await _edit_bot_message(bot_message_id, message_text, {"Отмена": 'cancel'})


async def _is_not_exists_room(message, room_number, keyboard_inline):
    message_text = (
        'Введенной комнаты не существует, или игра завершена.\n'
        'Введите корректный номер комнаты.'
    )
    
    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    
    logger.info(
        f'Incorrect room number [{room_number}] '
        f'from [{message.from_user.id}]'
    )


@router.message(JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message, state: FSMContext, session: Session):
    state_data = await state.get_data()
    wishes = message.text
    chat_id = message.chat.id
    room_number = state_data['room_number']
    bot_message = state_data.get('bot_message_id')
    
    await message.delete()
    
    await RoomRepo(session).add_member(
        user_id=chat_id,
        room_number=room_number
    )
    
    await WishRepo(session).create_or_update_wish_for_room(
        wish=wishes,
        user_id=chat_id,
        room_id=room_number
    )
    
    keyboard_inline = generate_inline_keyboard(
        {
            "В комнату ➡️": f"room_menu_{room_number}",
        }
    )
    message_text = (
        'Хо-хо-хо! 🎅\n\n'
        f'Вы вошли в комнату <b>{room_number}</b>.\n'
        'Теперь ты можешь играть с своими друзьями.\n'
        'Следи за анонсами владельца комнаты.\n\n'
        'Желаю хорошей игры! 😋'
    )
    
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    logger.info(
        f'The user[{message.from_user.id}] '
        f'successful subscribed to the room [{state_data["room_number"]}]'
    )
    await state.clear()

#
