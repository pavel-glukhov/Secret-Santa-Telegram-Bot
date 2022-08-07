from typing import Tuple
from app.database.models import User


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class

    async def create_user_or_get(self,
                                 username: str,
                                 user_id: int,
                                 **kwargs) -> Tuple[User, bool]:
        return await self._class.get_or_create(username=username,
                                               user_id=user_id,
                                               **kwargs)

    async def get_user_or_none(self, user_id: int) -> User:
        return await self._class.get_or_none(user_id=user_id)

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass