import logging

from aiogram import Router

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.communication_states import (MessageToRecipient,
                                                 MessageToSanta)

logger = logging.getLogger(__name__)
router = Router()


async def send_first_message_to_user(callback, state, lang, room_number, edit_message, recipient_type):
    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard({cancel_button: 'cancel'})

    if recipient_type == "recipient":
        message_text = lang.messages.communication_menu.message_to_recipient.first_msg
        next_state = MessageToRecipient.waiting_message
    else:
        message_text = lang.messages.communication_menu.message_to_sender.first_msg
        next_state = MessageToSanta.waiting_message

    if edit_message:
        initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)
    else:
        initial_bot_message = await callback.message.answer(text=message_text, reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message, room_number=room_number)
    await state.set_state(next_state)
