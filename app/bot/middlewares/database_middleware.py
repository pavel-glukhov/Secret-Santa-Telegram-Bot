from typing import Any, Awaitable, Callable, Generator

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import scoped_session


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory: Callable[[], Generator[scoped_session, None, None]]) -> None:
        self.session_factory = session_factory
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        session = next(self.session_factory())
        try:
            data["session"] = session
            return await handler(event, data)
        finally:
            session.remove()
