import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.communication.states import MessageToRecipient
from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.messages.send_messages import send_message
from app.store.database.queries.game_result import GameResultDB

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_closed-con-rec'))
async def message_to_recipient(callback: types.CallbackQuery):
    await MessageToRecipient.waiting_message.set()
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id
    

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
        'Напишите сообщение которое вы хотите отправить вашему получателю. 🙍‍♂️'
    )
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )


@dp.message_handler(
    state=MessageToRecipient.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext):
    state_data = await state.get_data()
    room_id = state_data['room_number']
    user_id = message.chat.id
    text = message.text
    recipient = await GameResultDB.get_recipient(room_id=room_id,
                                                 user_id=user_id)
    await send_message(user_id=recipient.user_id,
                       text=text)
    
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    
    message_text = 'Сообщение вашему получателю было отправлено'
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()