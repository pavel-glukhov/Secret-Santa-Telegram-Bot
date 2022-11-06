import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.bot import dispatcher as dp
from app.bot.handlers import texts
from app.store.database import room_db
from app.store.database.models import User
from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.handlers.operations import get_room_number

logger = logging.getLogger(__name__)


class ChangeOwner(StatesGroup):
    waiting_for_owner_name = State()


@dp.callback_query_handler(Text(startswith='room_change-owner'))
async def change_room_owner(callback: types.CallbackQuery):
    room_number = get_room_number(callback)
    await ChangeOwner.waiting_for_owner_name.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    keyboard_inline = generate_inline_keyboard(
        {
            "Отмена": 'cancel',
        }
    )

    await callback.message.answer(
        texts.CHANGE_MAIN_QUESTION,
        reply_markup=keyboard_inline
    )


@dp.message_handler(state=ChangeOwner.waiting_for_owner_name)
async def process_changing_owner(message: types.Message, state: FSMContext):
    state_data = await dp.current_state().get_data()
    room_number = state_data['room_number']
    previous_owner = message.chat.id
    new_owner = message.text

    keyboard_inline = generate_inline_keyboard(
        {
            "Вернуться назад ◀️": f"room_menu_{room_number}",
        }
    )

    owner: User = await room_db().change_owner(new_owner,
                                               room_number)

    logger.info(f'The owner ({previous_owner}) of room '
                f'"{room_number}" has been changed to "{owner.user_id}"')

    await state.finish()
    if owner:
        await message.answer(
            texts.CHANGE_COMPLETE_ANSWER.format(new_owner, ),
            reply_markup=keyboard_inline
        )
    else:
        await message.answer(
            texts.USER_NOT_FOUND,
            reply_markup=keyboard_inline
        )
