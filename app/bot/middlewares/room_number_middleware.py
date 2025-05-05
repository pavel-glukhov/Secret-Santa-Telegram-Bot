import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

class RoomNumberMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            room_number = int(event.data[event.data.rfind('_') + 1:])
            data["room_number"] = room_number
        except (ValueError, AttributeError):
            logger.warning("Failed to parse room number from callback data: %s", event.data)
            data["room_number"] = None

        return await handler(event, data)