import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.states.rooms import DeleteRoom
from app.store.database.queries.rooms import RoomRepo

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('room_delete'))
async def delete_room(callback: types.CallbackQuery,
                      state: FSMContext,
                      lang: TranslationMainSchema,
                      room_number: int):
    await state.update_data(room_number=room_number)
    await state.update_data(question_message_id=callback.message.message_id)
    cancel_button = lang.buttons.cancel_button

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'})

    message_text = lang.messages.rooms_menu.delete_room.delete_room_first_msg.format(
        room_number=room_number
    )

    initial_bot_message = await callback.message.edit_text(text=message_text,
                                                           reply_markup=keyboard_inline)

    await state.update_data(bot_message_id=initial_bot_message)
    await state.set_state(DeleteRoom.waiting_conformation)


@router.message(lambda message: message.text.lower() not in ['confirm'],
                StateFilter(DeleteRoom.waiting_conformation))
async def process_delete_room_invalid(message: types.Message,
                                      state: FSMContext,
                                      lang: TranslationMainSchema):
    state_data = await state.get_data()
    room_number = state_data['room_number']
    cancel_button = lang.buttons.cancel_button

    keyboard_inline = generate_inline_keyboard(
        {cancel_button: 'cancel'}
    )

    logger.info('Incorrect confirmation'
                f' command from [{message.from_user.id}]')
    await message.delete()
    bot_message = state_data['bot_message_id']

    message_text = lang.messages.rooms_menu.delete_room.error_command_verif.format(
        room_number=room_number
    )

    await bot_message.edit_text(
        text=message_text,
        reply_markup=keyboard_inline
    )


@router.message(lambda message: message.text.lower() in ['confirm'],
                StateFilter(DeleteRoom.waiting_conformation))
async def completed_process_delete_room(message: types.Message,
                                        state: FSMContext,
                                        session: Session,
                                        lang: TranslationMainSchema):
    state_data = await state.get_data()
    await message.delete()

    bot_message = state_data['bot_message_id']
    room_number = state_data['room_number']

    return_back_button = lang.buttons.return_back_button
    keyboard_inline = generate_inline_keyboard(
        {
            return_back_button: "root_menu",
        }
    )
    is_room_deleted = await RoomRepo(session).delete(room_number=room_number)

    if is_room_deleted:
        message_text = lang.messages.rooms_menu.delete_room.delete_room_second_msg
        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )

        logger.info(
            f'The user [{message.from_user.id}]'
            f' removed the room [{room_number}]'
        )
    else:
        message_text = lang.messages.rooms_menu.delete_room.error

        await bot_message.edit_text(
            text=message_text,
            reply_markup=keyboard_inline
        )
        logger.info(
            f'The room [{room_number}]'
            'was not removed removed'
            f' by[{message.from_user.id}] '
        )

    await state.clear()
