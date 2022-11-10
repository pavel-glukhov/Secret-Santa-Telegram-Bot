import asyncio
import logging

from aiogram.utils import exceptions

from app.bot import bot

logger = logging.getLogger(__name__)


async def send_message(user_id: int,
                       text: str,
                       disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text,
                               disable_notification=disable_notification)

    except exceptions.BotBlocked:
        logger.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded."
            f" Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logger.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
    else:
        logger.info(f"The message was sent to [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(list_users, text) -> int:
    """
    broadcaster
    :return: Count of messages
    """
    count = 0
    try:
        for user_id in list_users:
            if await send_message(user_id, text):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second
    finally:
        logger.info(f"{count} messages successful sent.")

    return count
