import asyncio
import logging

from aiogram.exceptions import (TelegramAPIError, TelegramForbiddenError,
                                TelegramRetryAfter)

from app.bot.keyborads.common import generate_inline_keyboard
from app.bot.languages import TranslationMainSchema
from app.bot.loader import bot

logger = logging.getLogger(__name__)


# TODO сделать что бы при отправке сообщений были разные кнопки.
async def send_message(user_id: int,
                       text: str,
                       inline_keyboard: dict,
                       disable_notification: bool = False,
                       **kwargs) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param player_language:
    :param inline_keyboard:
    :param disable_notification:
    :return:
    """
    keyboard_inline = generate_inline_keyboard(
        inline_keyboard
    )
    try:
        await bot.send_message(user_id, text,
                               disable_notification=disable_notification,
                               reply_markup=keyboard_inline,
                               **kwargs)
    
    except TelegramForbiddenError:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except TelegramRetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded."
            f" Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await send_message(user_id, text, inline_keyboard)  # Recursive call
    
    except TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.info(f"The message was sent to [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(list_users: list) -> None:
    """
    broadcaster
    :return: Count of messages
    """
    count = 0
    try:
        for user in list_users:
            if await send_message(user_id=user['user_id'],
                                  text=user['text'],
                                  inline_keyboard={user['player_language'].menu_button: "start_menu"}):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second
    finally:
        logger.info(f"{count} messages successful sent.")
