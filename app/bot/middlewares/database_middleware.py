from typing import Any, Awaitable, Callable, AsyncGenerator
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_scoped_session

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory: Callable[[], AsyncGenerator[async_scoped_session, None]]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)