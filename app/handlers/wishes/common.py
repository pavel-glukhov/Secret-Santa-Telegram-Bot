from typing import Union

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from app import dispatcher as dp


class ChangeWish(StatesGroup):
    waiting_for_wishes = State()


# TODO Написать изменение пожелания
async def update_wishes(message: types.Message,
                        room_number: Union[str, int]):
    await ChangeWish.waiting_for_wishes.set()
    state = dp.get_current().current_state()
    await state.update_data(room_number=room_number)

    # TODO добавить получение текущего пожелания
    # get user's wishes

    await message.edit_text(f'',
                            parse_mode=ParseMode.MARKDOWN)
