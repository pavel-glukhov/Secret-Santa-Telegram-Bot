import logging

from aiogram import Router

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.communication import MessageToRecipient
from app.bot.states.communication import MessageToSanta

logger = logging.getLogger(__name__)
router = Router()


async def send_answer(callback, state, app_text_msg, edit_message, recipient_type):
    cancel_button = app_text_msg.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard({cancel_button: 'cancel'})

    if recipient_type == "recipient":
        message_text = app_text_msg.messages.communication_menu.message_to_recipient.first_msg
        next_state = MessageToRecipient.waiting_message
    else:
        message_text = app_text_msg.messages.communication_menu.message_to_sender.first_msg
        next_state = MessageToSanta.waiting_message

    if edit_message:
        initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    else:
        initial_bot_message = await callback.message.answer(text=message_text, reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message, room_number=get_room_number(callback))
    await state.set_state(next_state)
