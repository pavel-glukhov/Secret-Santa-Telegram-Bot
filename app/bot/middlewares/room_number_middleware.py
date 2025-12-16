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
        data["room_number"] = None

        if event.data and '_' in event.data:
            potential_number = event.data.rsplit('_', 1)[-1]
            try:
                data["room_number"] = int(potential_number)
            except ValueError:
                logger.warning(
                    "Failed to parse room number from callback data: %s", event.data
                )

        return await handler(event, data)