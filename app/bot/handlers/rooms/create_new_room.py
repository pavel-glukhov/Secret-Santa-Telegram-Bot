import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from app.bot.languages import TranslationMainSchema

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.states.rooms import CreateRoom
from app.config import load_config
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_create_new_room')
async def create_room(callback: types.CallbackQuery,
                      state: FSMContext,
                      session: Session,
                      app_text_msg: TranslationMainSchema):
    count_user_rooms = await RoomRepo(session).get_count_user_rooms(
        callback.message.chat.id)
    logger.info(count_user_rooms)
    if count_user_rooms >= load_config().room.user_rooms_count:
        keyboard_inline = generate_inline_keyboard(
            {
                app_text_msg.buttons.return_back_button: "root_menu",
            }
        )
        message_text = app_text_msg.messages.rooms_menu.create_new_room.limit.format(
            maximal_count_rooms=load_config().room.user_rooms_count
        )

        return await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )

    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'})
    message_text = app_text_msg.messages.rooms_menu.create_new_room.create_new_room_first_msg

    initial_bot_message = await callback.message.edit_text(text=message_text, reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(CreateRoom.waiting_for_room_name)


@router.message(CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message,
                       state: FSMContext,
                       app_text_msg: TranslationMainSchema):
    room_name = message.text
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    await state.update_data(room_name=room_name)
    await state.update_data(budget_question_id=message.message_id)
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'})

    if not len(room_name) > 16:
        keyboard_inline = generate_inline_keyboard(
            {app_text_msg.buttons.cancel_button: 'cancel'})
        message_text = app_text_msg.messages.rooms_menu.create_new_room.long_room_name

        return await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)
    await state.set_state(CreateRoom.waiting_for_room_budget)

    message_text = app_text_msg.messages.rooms_menu.create_new_room.create_new_room_second_msg.format(
        room_name=room_name
    )
    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(CreateRoom.waiting_for_room_budget))
async def process_budget_invalid(message: types.Message,
                                 state: FSMContext,
                                 app_text_msg: TranslationMainSchema):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')

    message_text = app_text_msg.messages.rooms_menu.create_new_room.long_budget

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message,
                         state: FSMContext, app_text_msg: TranslationMainSchema):
    await state.update_data(wishes_question_message_id=message.message_id)
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.cancel_button: 'cancel'})
    room_budget = message.text
    await state.update_data(room_budget=room_budget)

    await state.set_state(CreateRoom.waiting_for_room_wishes)
    message_text = app_text_msg.messages.rooms_menu.create_new_room.create_new_room_third_msg.format(
        room_budget=room_budget
    )

    await bot_message.edit_text(text=message_text, reply_markup=keyboard_inline)


@router.message(CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message, state: FSMContext, session: Session,
                         app_text_msg: TranslationMainSchema):
    user_wishes = message.text
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {app_text_msg.buttons.room_menu.main_buttons.menu: 'root_menu'}
    )

    room = await RoomRepo(session).create(user_wish=user_wishes,
                                          owner_id=message.chat.id,
                                          name=state_data['room_name'],
                                          budget=state_data['room_budget'])

    logger.info(
        f'The new room "{room.number}" has been created by {message.chat.id}'
    )
    message_text = app_text_msg.messages.rooms_menu.create_new_room.create_new_room_forth_msg.format(
        room_name=room.name,
        room_number=room.number
    )

    await bot_message.edit_text(text=message_text)
    message_text = app_text_msg.messages.rooms_menu.create_new_room.create_new_room_additional_msg

    await bot_message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.clear()
