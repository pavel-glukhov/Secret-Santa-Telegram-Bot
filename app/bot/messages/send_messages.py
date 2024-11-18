import asyncio
import logging

from aiogram.exceptions import (TelegramAPIError, TelegramForbiddenError,
                                TelegramRetryAfter)
from aiohttp import ClientError

from app.bot.loader import bot

logger = logging.getLogger(__name__)


async def send_message(user_id: int,
                       text: str,
                       disable_notification: bool = False,
                       **kwargs) -> bool:
    """
    Safe messages sender
    :param user_id: ID of the user to send the message to.
    :param text: Text of the message.
    :param inline_keyboard: Inline keyboard configuration.
    :param disable_notification: Whether to disable notifications.
    :return: True if the message was sent successfully, False otherwise.
    """
    try:
        await bot.send_message(user_id, text,
                               disable_notification=disable_notification,
                               **kwargs)
    except TelegramForbiddenError:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except TelegramRetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await send_message(user_id, text, **kwargs)
    except ClientError:
        logger.error(f"Target [ID:{user_id}]: Network error occurred.")
        await asyncio.sleep(5)
        return await send_message(user_id, text, **kwargs)
    except TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.info(f"The message was sent to [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(list_users: list) -> None:
    """
    Broadcast messages to a list of users.
    :param list_users: List of users to send messages to.
    """
    count = 0
    tasks = []
    try:
        for user in list_users:
            tasks.append(send_message(user_id=user['user_id'],
                                      text=user['text'],
                                      reply_markup={user['player_language'].buttons.menu: "start_menu"}))
            await asyncio.sleep(.05)  # 20 messages per second
        results = await asyncio.gather(*tasks)
        count = sum(results)
    finally:
        logger.info(f"{count} messages successfully sent.")
