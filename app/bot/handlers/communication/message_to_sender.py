import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.communication.general_first_message import \
    send_first_message_to_user
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.loader import language_return_dataclass
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.communication.telegram_messaging import safe_send_message
from app.bot.states.communication_states import MessageToSanta
from app.store.database.repo.communication import CommunicationRepo
from app.store.database.repo.game_result import GameResultRepo
from app.store.database.repo.rooms import RoomRepo
from app.store.database.repo.users import UserRepo
from app.store.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_closed-con-san_no_ed'))
async def message_to_santa_no_edit(callback: types.CallbackQuery,
                                   state: FSMContext,
                                   lang: TranslationMainSchema,
                                   room_number: int):
    await message_to_santa(callback, state, lang, edit_message=False)


@router.callback_query(F.data.startswith('room_closed-con-san'))
async def message_to_santa(callback: types.CallbackQuery,
                           state: FSMContext,
                           lang: TranslationMainSchema,
                           room_number: int,
                           edit_message=True):
    await send_first_message_to_user(callback, state, lang, room_number, edit_message, "sender")


@router.message(MessageToSanta.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext, session: Session,
                                     lang: TranslationMainSchema):
    state_data = await state.get_data()
    user_id = message.chat.id
    room = await RoomRepo(session).get(state_data['room_number'])

    await message.delete()

    bot_message = state_data['bot_message_id']
    sender = await GameResultRepo(session).get_sender(room_id=room.number,
                                                      user_id=user_id)

    sender_language = await UserRepo(session).get_user_language(sender.user_id)
    sender_app_lng = await language_return_dataclass(get_redis_client(), sender_language)

    first_message_text = sender_app_lng.messages.communication_menu.message_to_sender.msg_text.format(
        room_name=room.name,
        room_number=room.number,
        text_message=message.text
    )

    reply_button = sender_app_lng.buttons.reply
    menu_button = sender_app_lng.buttons.menu
    inline_keyboard = {
        reply_button: f"room_closed-con-rec_{room.number}",
        menu_button: "root_menu"
    }

    await CommunicationRepo(session).insert(
        recipient_id=sender.user_id,
        sender_id=user_id,
        room=room,
        message=message.text
    )
    await safe_send_message(user_id=sender.user_id,
                            text=first_message_text,
                            )
    await safe_send_message(user_id=sender.user_id,
                            text=sender_app_lng.messages.main_menu.allowed_actions,
                            reply_markup=generate_inline_keyboard(inline_keyboard)
                            )
    second_message_text = lang.messages.communication_menu.message_to_sender.msg_was_sent

    keyboard_inline = generate_inline_keyboard(
        {
            lang.buttons.return_back_button: "root_menu",
        }
    )
    await bot_message.edit_text(text=second_message_text, reply_markup=keyboard_inline)
    await state.clear()
