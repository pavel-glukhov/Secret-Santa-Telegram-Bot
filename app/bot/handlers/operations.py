import logging

from aiogram import exceptions, types

logger = logging.getLogger(__name__)


def get_room_number(callback: types.CallbackQuery) -> int:
    """
    Gets the room number from callback data
    :param callback:
    :return:
    """
    try:
        room_number = int(callback.data[callback.data.rfind('_') + 1:])
        return room_number
    except ValueError:
        return False


