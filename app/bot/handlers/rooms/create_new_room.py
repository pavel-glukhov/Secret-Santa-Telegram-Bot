import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages.schemes import TranslationMainSchema
from app.bot.states.rooms_states import CreateRoom
from app.config import load_config
from app.store.database.repo.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'menu_create_new_room')
async def create_room(callback: types.CallbackQuery,
                      state: FSMContext,
                      session: AsyncSession,
                      lang: TranslationMainSchema):
    user_id = callback.message.chat.id
    user_rooms_limit = load_config().room.user_rooms_count

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})

    count_user_rooms = await RoomRepo(session).get_count_user_rooms(
        user_id)

    if count_user_rooms >= user_rooms_limit:
        return_back_button = lang.buttons.return_back_button
        keyboard_inline = generate_inline_keyboard(
            {
                return_back_button: "root_menu",
            }
        )
        message_text = lang.messages.rooms_menu.create_new_room.limit.format(
            maximal_count_rooms=user_rooms_limit
        )

        return await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )

    message_text = lang.messages.rooms_menu.create_new_room.create_new_room_first_msg

    initial_bot_message = await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(CreateRoom.waiting_for_room_name)


@router.message(CreateRoom.waiting_for_room_name)
async def process_name(message: types.Message,
                       state: FSMContext,
                       lang: TranslationMainSchema):
    room_name = message.text
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    await state.update_data(room_name=room_name)
    await state.update_data(budget_question_id=message.message_id)

    cancel_button = lang.buttons.cancel_button
    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})

    if not len(room_name) < 17:
        cancel_button = lang.buttons.cancel_button

        keyboard_inline = generate_inline_keyboard(
            {cancel_button: 'cancel'})
        message_text = lang.messages.rooms_menu.create_new_room.long_room_name

        return await bot_message.edit_text(text=message_text,
                                           reply_markup=keyboard_inline)
    await state.set_state(CreateRoom.waiting_for_room_budget)

    message_text = lang.messages.rooms_menu.create_new_room.create_new_room_second_msg.format(
        room_name=room_name
    )
    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.message(lambda message:
                len(message.text.lower()) > 16,
                StateFilter(CreateRoom.waiting_for_room_budget))
async def process_budget_invalid(message: types.Message,
                                 state: FSMContext,
                                 lang: TranslationMainSchema):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    cancel_button = lang.buttons.cancel_button

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})
    logger.info('long budget message'
                f' command from [{message.from_user.id}] ')

    message_text = lang.messages.rooms_menu.create_new_room.long_budget

    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.message(CreateRoom.waiting_for_room_budget)
async def process_budget(message: types.Message,
                         state: FSMContext,
                         lang: TranslationMainSchema):
    await state.update_data(wishes_question_message_id=message.message_id)
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    cancel_button = lang.buttons.cancel_button

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})
    room_budget = message.text
    await state.update_data(room_budget=room_budget)

    await state.set_state(CreateRoom.waiting_for_room_wishes)
    message_text = lang.messages.rooms_menu.create_new_room.create_new_room_third_msg.format(
        room_budget=room_budget
    )

    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.message(CreateRoom.waiting_for_room_wishes)
async def process_wishes(message: types.Message,
                         state: FSMContext,
                         session: AsyncSession,
                         lang: TranslationMainSchema):
    user_wishes = message.text
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    keyboard_inline = generate_inline_keyboard(
        {lang.buttons.room_menu.main_buttons.menu: 'root_menu'}
    )

    room = await RoomRepo(session).create(user_wish=user_wishes,
                                          owner_id=message.chat.id,
                                          name=state_data['room_name'],
                                          budget=state_data['room_budget'])

    logger.info(
        f'The new room "{room.number}" has been created by {message.chat.id}'
    )
    message_text = lang.messages.rooms_menu.create_new_room.create_new_room_forth_msg.format(
        room_name=room.name,
        room_number=room.number
    )

    await bot_message.edit_text(text=message_text)
    message_text = lang.messages.rooms_menu.create_new_room.create_new_room_additional_msg

    await bot_message.answer(
        text=message_text,
        reply_markup=keyboard_inline,
    )
    await state.clear()
