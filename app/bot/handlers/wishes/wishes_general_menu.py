import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.handlers.operations import get_room_number
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.states.wishes import ChangeWish
from app.store.database.queries.rooms import RoomRepo
from app.store.database.queries.wishes import WishRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_show-wish'))
async def show_wishes(callback: types.CallbackQuery,
                      session: Session,
                      app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    message = callback.message
    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.wishes_menu.change_wish: f"room_change-wish_{room_number}",
            app_text_msg.buttons.return_back_button: f"room_menu_{room_number}",

        }
    )

    user_id = message.chat.id
    wishes = await WishRepo(session).get(user_id, room_number)

    message_text = app_text_msg.messages.wishes_menu.your_wishes.format(
        wishes=wishes
    )
    await message.edit_text(text=message_text,
                            reply_markup=keyboard_inline)


@router.callback_query(F.data.startswith('room_change-wish'))
async def update_wishes(callback: types.CallbackQuery,
                        state: FSMContext,
                        app_text_msg: TranslationMainSchema):
    room_number = get_room_number(callback)
    await state.update_data(room_number=room_number)
    cancel_button = app_text_msg.buttons.cancel_button
    
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    message_text = app_text_msg.messages.wishes_menu.new_wishes

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(ChangeWish.waiting_for_wishes)


@router.message(ChangeWish.waiting_for_wishes)
async def process_updating_wishes(
        message: types.Message,
        state: FSMContext,
        session: Session,
        app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    bot_message = state_data['bot_message_id']
    wish = message.text
    user_id = message.chat.id

    await message.delete()

    keyboard_inline = generate_inline_keyboard(
        {
            app_text_msg.buttons.return_back_button: f"room_menu_{room_number}",
        }
    )
    await WishRepo(session).create_or_update_wish_for_room(
        wish=wish,
        user_id=user_id,
        room_id=room_number
    )

    room = await RoomRepo(session).get(room_number)
    await state.clear()

    message_text = app_text_msg.messages.wishes_menu.changed_wishes.format(
        room_name=room.name, wish=wish
    )
    await bot_message.edit_text(text=message_text,
                                reply_markup=keyboard_inline)
