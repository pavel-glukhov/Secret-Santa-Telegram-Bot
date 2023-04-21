import logging

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters import Text
from app.bot import dispatcher as dp
from app.bot.handlers.communication.states import MessageToSanta
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.messages.send_messages import send_message
from app.store.database.queries.game_result import GameResultDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_closed-con-san'))
async def message_to_santa(callback: types.CallbackQuery):
    await MessageToSanta.waiting_message.set()
    room_number = get_room_number(callback)
    state = dp.get_current().current_state()
    await state.update_data(
        room_number=room_number,
    )
    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )
    message_text = (
        'Напишите сообщение которое вы хотите '
        'отправить вашему Тайному Санте. 🎅'
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(
    state=MessageToSanta.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext):
    state_data = await state.get_data()
    user_id = message.chat.id
    room_id = state_data['room_number']
    text = message.text
    sender = await GameResultDB.get_sender(room_id=room_id,
                                           user_id=user_id)
    await send_message(user_id=sender.user_id,
                       text=text)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    
    message_text = 'Сообщение вашему Санте было отправлено'
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()