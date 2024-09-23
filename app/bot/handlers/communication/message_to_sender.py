import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema, language_return_dataclass
from app.bot.messages.send_messages import send_message
from app.bot.states.communication import MessageToSanta
from app.store.database.queries.communication import CommunicationRepo
from app.store.database.queries.game_result import GameResultRepo
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.users import UserRepo
from app.store.redis import get_redis_client

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_closed-con-san_no_ed'))
async def message_to_santa_no_edit(callback: types.CallbackQuery,
                                   state: FSMContext,
                                   app_text_msg: TranslationMainSchema):
    await message_to_santa(callback, state, app_text_msg, edit_message=False)


@router.callback_query(F.data.startswith('room_closed-con-san'))
async def message_to_santa(callback: types.CallbackQuery,
                           state: FSMContext,
                           app_text_msg: TranslationMainSchema,
                           edit_message=True):
    room_number = get_room_number(callback)
    await state.update_data(
        room_number=room_number,
    )
    cancel_button = app_text_msg.buttons.cancel_button
    
    keyboard_inline = generate_inline_keyboard(
        {
            cancel_button: 'cancel',
        }
    )
    message_text = app_text_msg.messages.communication_menu.message_to_sender.first_msg
    
    if edit_message:
        initial_bot_message = await callback.message.edit_text(text=message_text,
                                                               reply_markup=keyboard_inline)
    else:
        initial_bot_message = await callback.message.answer(text=message_text,
                                                            reply_markup=keyboard_inline)
    
    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(MessageToSanta.waiting_message)


@router.message(MessageToSanta.waiting_message)
async def completed_message_to_santa(message: types.Message,
                                     state: FSMContext, session: Session,
                                     app_text_msg: TranslationMainSchema):
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
        text_message=message.text)
    
    inline_keyboard = {
        sender_app_lng.buttons.reply: f"room_closed-con-rec_{room.number}",
        sender_app_lng.buttons.menu: "root_menu"
    }
    await CommunicationRepo(session).insert(
        recipient_id=sender.user_id,
        sender_id=user_id,
        room=room,
        message=message.text

    )
    await send_message(user_id=sender.user_id,
                       text=first_message_text,
                       )
    await send_message(user_id=sender.user_id,
                       text=sender_app_lng.messages.main_menu.allowed_actions,
                       reply_markup=generate_inline_keyboard(inline_keyboard)
                       )
    second_message_text = app_text_msg.messages.communication_menu.message_to_sender.msg_was_sent
    
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: "root_menu",
        }
    )
    await bot_message.edit_text(text=second_message_text, reply_markup=keyboard_inline)
    await state.clear()
