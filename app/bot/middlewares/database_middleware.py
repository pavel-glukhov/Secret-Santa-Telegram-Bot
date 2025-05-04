from contextlib import AbstractContextManager
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import scoped_session


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory: Callable[[], AbstractContextManager[scoped_session]]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)