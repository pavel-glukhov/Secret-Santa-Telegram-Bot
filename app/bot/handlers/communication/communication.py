import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher.filters import Text
from app.bot import dispatcher as dp

logger = logging.getLogger(__name__)


class MessageToSanta(StatesGroup):
    waiting_message = State()


class MessageToRecipient(StatesGroup):
    waiting_message = State()

#TODO дописать по коммуникации
@dp.callback_query_handler(Text(startswith='room_closed-con-san'))
async def message_to_santa(callback: types.CallbackQuery):
    pass


@dp.callback_query_handler(Text(startswith='room_closed-con-rec'))
async def message_to_recipient(callback: types.CallbackQuery):
    pass
