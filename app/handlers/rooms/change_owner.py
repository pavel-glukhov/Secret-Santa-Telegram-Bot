from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from app.keyborads.constants import MAIN_BUTTONS
from app import dispatcher as dp
from app import room_db
from app.keyborads.common import create_common_keyboards


class ChangeOwner(StatesGroup):
    waiting_for_owner_name = State()


async def change_room_owner(message: types.Message, room_number):
    pass
