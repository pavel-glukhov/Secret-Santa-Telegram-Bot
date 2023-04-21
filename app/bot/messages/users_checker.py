import asyncio
import logging

from aiogram.utils import exceptions

from app.bot import bot
from app.store.database.queries.users import UserDB

logger = logging.getLogger(__name__)


async def checking_user_is_active(user_id):
    """
    Checking if a bot was blocked by user
    or user's chat is not existing by other reason.
    """
    try:
        await bot.send_chat_action(user_id, action='typing')

    except exceptions.BotBlocked:
        logger.error(f"The bot was blocked by user [ID:{user_id}]")
        await UserDB.disable_user(user_id)
        return False

    except exceptions.UserDeactivated:
        logger.error(f"The user [ID:{user_id}] is deactivated")
        await UserDB.disable_user(user_id)
        return False

    except exceptions.ChatNotFound:
        logger.error(f"Target [ID:{user_id}]: invalid user ID")
        await UserDB.disable_user(user_id)
        return False

    except exceptions.RetryAfter as e:
        logger.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded."
            f" Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return False

    except exceptions.TelegramAPIError:
        logger.exception(f"Target [ID:{user_id}]: failed")
        return False

    return True

