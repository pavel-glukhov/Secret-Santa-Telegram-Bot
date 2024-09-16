import logging

from aiogram import F, Router, types
from sqlalchemy.orm import Session
from app.bot.languages import TranslationMainSchema

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_exit'))
async def left_room(callback: types.CallbackQuery,
                    session: Session,
                    app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    user_id = callback.message.chat.id
    await RoomRepo(session).remove_member(user_id, room_number)

    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: "root_menu",
        }
    )
    message_text = app_text_msg.messages.rooms_menu.unsubscribe.unsubscribe_first_msg.format(
        room_number=room_number
    )

    await callback.message.edit_text(
        text=message_text,
    )
    message_text = app_text_msg.messages.rooms_menu.unsubscribe.unsubscribe_second_msg.format(
        room_number=room_number
    )

    await callback.message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    logger.info(
        f'The user[{callback.message.chat.id}]'
        f' left from the room[{room_number}]'
    )
