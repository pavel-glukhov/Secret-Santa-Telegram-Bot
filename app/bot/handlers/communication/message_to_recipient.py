import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.communication.general_first_message import send_first_message_to_user
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema, language_return_dataclass
from app.bot.messages.send_messages import send_message
from app.bot.states.communication import MessageToRecipient
from app.store.database.queries.communication import CommunicationRepo
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.users import UserRepo
from app.store.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_closed-con-rec_no_ed'))
async def message_to_santa_no_edit(callback: types.CallbackQuery,
                                   state: FSMContext,
                                   app_text_msg: TranslationMainSchema):
    await message_to_recipient(callback, state, app_text_msg, edit_message=False)


@router.callback_query(F.data.startswith('room_closed-con-rec'))
async def message_to_recipient(callback: types.CallbackQuery, state: FSMContext,
                               app_text_msg: TranslationMainSchema, edit_message=True):
    await send_first_message_to_user(callback, state, app_text_msg, edit_message, "recipient")


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
    recipient_language = await UserRepo(session).get_user_language(recipient.user_id)
    recipient_app_lng = await language_return_dataclass(get_redis_client(), recipient_language)

    first_message_text = recipient_app_lng.messages.communication_menu.message_to_recipient.msg_text.format(
        room_name=room.name,
        room_number=room.number,
        text_message=message.text,
    )
    inline_keyboard = {
        recipient_app_lng.buttons.reply: f"room_closed-con-san_{room.number}",
        recipient_app_lng.buttons.menu: "root_menu"
    }
    await CommunicationRepo(session).insert(
        recipient_id=recipient.user_id,
        sender_id=user_id,
        room=room,
        message=message.text

    )
    await send_message(user_id=recipient.user_id,
                       text=first_message_text,
                       )
    await send_message(user_id=recipient.user_id,
                       text=recipient_app_lng.messages.main_menu.allowed_actions,
                       reply_markup=generate_inline_keyboard(inline_keyboard)
                       )
    second_message_text = app_text_msg.messages.communication_menu.message_to_recipient.msg_was_sent

    await bot_message.edit_text(text=second_message_text, reply_markup=keyboard_inline)
    await state.clear()
