import logging
import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import (create_common_keyboards,
                                      generate_inline_keyboard)
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.rooms_states import JoinRoom
from app.core.database.repo.rooms import RoomRepo
from app.core.database.repo.wishes import WishRepo

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.regexp(r"^inv_wlc_msg_(\d+)$"))
async def join_to_room_inv_welcome_message(event: types.Message | types.CallbackQuery,
                                        lang,
                                        session,
                                        room_id=None):
    if not room_id:
        data = event.data
        match = re.match(r"^inv_wlc_msg_(\d+)$", data)
        room_id = int(match.group(1))

    room = await RoomRepo(session).get(room_number=room_id)
    keyboard_inline = generate_inline_keyboard(
        {lang.buttons.enter_to_joined_room: f'room_invite_{room_id}'}
    )

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text=lang.messages.rooms_menu.subscribe.room_invitation.format(
        room_name=room.name,
        room_id=room_id),
        reply_markup=keyboard_inline)
        await event.answer()
    else:
        await event.answer(text=lang.messages.rooms_menu.subscribe.room_invitation.format(
        room_name=room.name,
        room_id=room_id),
        reply_markup=keyboard_inline)


@router.callback_query(F.data.regexp(r"^room_invite_(\d+)$"))
async def room_invitation(callback: types.CallbackQuery,
                                   state: FSMContext,
                                   lang: TranslationMainSchema,
                                   session: AsyncSession):
    data = callback.data
    match = re.match(r"^room_invite_(\d+)$", data)
    room_number = match.group(1)
    cancel_button = lang.buttons.cancel_button
    room = await RoomRepo(session).get(room_number=int(room_number))

    if not room or room.is_closed:
        await callback.message.answer(
            lang.messages.rooms_menu.subscribe.room_is_not_exist_or_closed_invitation
        )
        return None

    members = [user.user_id for user in room.members]
    if callback.message.chat.id in members:
        await callback.answer()
        await callback.message.answer(lang.messages.rooms_menu.subscribe.already_joined)
        return None

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    message_text = lang.messages.rooms_menu.subscribe.subscribe_second_msg

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    await state.update_data(bot_message_id=initial_bot_message)
    await state.update_data(room_number=room_number)
    await state.set_state(JoinRoom.waiting_for_wishes)


@router.callback_query(F.data.in_(['menu_join_room']))
async def join_room(callback: types.CallbackQuery,
                    state: FSMContext,
                    lang: TranslationMainSchema):
    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )
    message_text = lang.messages.rooms_menu.subscribe.subscribe_first_msg
    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(JoinRoom.waiting_for_room_number)


@router.message(JoinRoom.waiting_for_room_number)
async def process_room_number(message: types.Message,
                              state: FSMContext,
                              session: AsyncSession,
                              lang: TranslationMainSchema):
    room_number = message.text
    state_data = await state.get_data()
    await state.update_data(room_number=room_number)
    bot_message_id = state_data.get('bot_message_id')

    await message.delete()

    if not room_number.isdigit():
        text_message = lang.messages.rooms_menu.subscribe.number_error
        cancel_button = lang.buttons.cancel_button

        return await _edit_bot_message(
            bot_message_id,
            text_message,
            {cancel_button: 'cancel'}
        )

    room = await RoomRepo(session).get(room_number=int(room_number))
    cancel_button = lang.buttons.cancel_button

    if not room or room.is_closed:
        return await _is_not_exists_room(bot_message_id,
                                         room_number,
                                         {cancel_button: 'cancel'},
                                         lang)

    is_member_of_room = await RoomRepo(session).is_member(
        user_id=message.chat.id,
        room_number=int(room_number)
    )

    if is_member_of_room:
        await _handle_existing_member(
            bot_message_id,
            message,
            state,
            session,
            room_number,
            lang
        )
    else:
        await _request_wishes(
            bot_message_id,
            state,
            lang,
            lang
        )


async def _edit_bot_message(bot_message_id,
                            text,
                            buttons):
    keyboard_inline = generate_inline_keyboard(buttons)
    await bot_message_id.edit_text(
        text=text,
        reply_markup=keyboard_inline
    )


async def _handle_existing_member(
        bot_message_id,
        message,
        state, session,
        room_number,
        language):
    keyboard_inline = await create_common_keyboards(message, session, language)

    await _edit_bot_message(
        bot_message_id,
        language.messages.rooms_menu.subscribe.already_joined,
        keyboard_inline
    )

    logger.info(
        f'The user[{message.from_user.id}] already is a member of the room [{room_number}]')
    await state.clear()


async def _request_wishes(bot_message_id,
                          state,
                          text,
                          lang):
    await state.set_state(JoinRoom.waiting_for_wishes)

    message_text = text.messages.rooms_menu.subscribe.subscribe_second_msg
    cancel_button = lang.buttons.cancel_button

    await _edit_bot_message(bot_message_id,
                            message_text,
                            {cancel_button: 'cancel'})


async def _is_not_exists_room(message,
                              room_number,
                              keyboard_inline,
                              text):
    message_text = text.messages.rooms_menu.subscribe.room_is_not_exist_or_closed

    await message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline,
    )

    logger.info(
        f'Incorrect room number [{room_number}] '
        f'from [{message.from_user.id}]'
    )


@router.message(JoinRoom.waiting_for_wishes)
async def process_room_wishes(message: types.Message,
                              state: FSMContext,
                              session: AsyncSession,
                              lang: TranslationMainSchema):
    state_data = await state.get_data()
    wishes = message.text
    chat_id = message.chat.id
    room_number = int(state_data['room_number'])
    bot_message = state_data.get('bot_message_id')

    await message.delete()

    await RoomRepo(session).add_member(
        user_id=chat_id,
        room_number=room_number,
        user_wish=wishes
    )

    await WishRepo(session).create_or_update_wish_for_room(
        wish=wishes,
        user_id=chat_id,
        room_id=room_number
    )

    to_room_button = lang.buttons.room_menu.subscribe.to_room
    keyboard_inline = generate_inline_keyboard(
        {
            to_room_button: f"room_menu_{room_number}",
        }
    )
    message_text = lang.messages.rooms_menu.subscribe.subscribe_third_msg.format(
        room_number=room_number
    )

    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )
    logger.info(
        f'The user[{message.from_user.id}] '
        f'successful subscribed to the room [{state_data["room_number"]}]'
    )
    await state.clear()
