from aiogram import types


def get_room_number(callback: types.CallbackQuery) -> int:
    """
    Gets the room number from callback data
    :param callback:
    :return:
    """
    return int(callback.data[callback.data.rfind('_') + 1:])
