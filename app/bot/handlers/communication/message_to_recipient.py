import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.messages.send_messages import send_message
from app.bot.states.communication import MessageToRecipient
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_closed-con-rec'))
async def message_to_recipient(callback: types.CallbackQuery,
                               state: FSMContext,
                               app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    await state.update_data(
        room_number=room_number,
    )
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.cancel_button: 'cancel',
        }
    )
    message_text = app_text_msg.messages.communication_menu.message_to_recipient.first_msg
    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(MessageToRecipient.waiting_message)


@router.message(MessageToRecipient.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext,
                                     session: Session,
                                     app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    room = await RoomRepo(session).get(state_data['room_number'])
    user_id = message.chat.id

    await message.delete()

    bot_message = state_data['bot_message_id']
    recipient = await GameResultRepo(session).get_recipient(room_id=room.number,
                                                            user_id=user_id)
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: "root_menu",
        }
    )
    first_message_text = app_text_msg.messages.communication_menu.message_to_recipient.msg_text.format(
        room_name=room.name,
        room_number=room.number,
        text_message=message.text,
    )
    await send_message(user_id=recipient.user_id,
                       text=first_message_text)
    second_message_text = app_text_msg.messages.communication_menu.message_to_recipient.msg_was_sent

    await bot_message.edit_text(text=second_message_text, reply_markup=keyboard_inline)
    await state.clear()
