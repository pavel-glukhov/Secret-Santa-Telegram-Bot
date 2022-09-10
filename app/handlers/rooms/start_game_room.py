import logging

from aiogram import types

from app.utils.send_messages import broadcaster

logger = logging.getLogger(__name__)


# TODO реализовать
async def start_game(message: types.Message, room_number):
    await broadcaster(room_number)


# TODO реализовать
async def process_waiting_datetime(message: types.Message):
    pass
