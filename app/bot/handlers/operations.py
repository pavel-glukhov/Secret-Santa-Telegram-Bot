import logging

from aiogram import types
from aiogram.utils import exceptions

from app.bot import bot

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


async def delete_user_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except exceptions.MessageToDeleteNotFound:
        logger.error(f'Message to be delete {message_id}  not found.')
    except exceptions.MessageCantBeDeleted:
        logger.error(f'Message {message_id}  cannot be deleted.')
