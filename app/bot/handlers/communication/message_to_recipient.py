import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.bot import dispatcher as dp
from app.bot.handlers.communication.states import MessageToRecipient
from app.bot.handlers.operations import delete_user_message, get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.messages.send_messages import send_message
from app.store.queries.game_result import GameResultRepo
from app.store.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text(startswith='room_closed-con-rec'))
async def message_to_recipient(callback: types.CallbackQuery):
    await MessageToRecipient.waiting_message.set()
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
        'Напишите сообщение которое вы хотите отправить вашему получателю. 🙍‍♂️'
    )
    async with state.proxy() as data:
        data['last_message'] = await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )


@dp.message_handler(state=MessageToRecipient.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext):
    state_data = await state.get_data()
    room = await RoomRepo().get(state_data['room_number'])
    user_id = message.chat.id
    last_message = state_data['last_message']
    recipient = await GameResultRepo().get_recipient(room_id=room.number,
                                                     user_id=user_id)
    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": "root_menu",
        }
    )
    text = (
        f'<b>Сообщение от Тайного Санты:</b>\n'
        f'Комната: {room.name} {[room.number]}\n'
        f'------------\n\n'
        f'{message.text}\n\n'
        f'------------\n\n'
    )
    await delete_user_message(message.from_user.id, message.message_id)
    await send_message(user_id=recipient.user_id,
                       text=text)
    
    message_text = 'Сообщение вашему получателю было отправлено'
    
    await last_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.finish()
