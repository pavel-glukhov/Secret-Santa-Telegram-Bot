from typing import Tuple, Union

from tortoise.expressions import Q

from app.database.models import User


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class

    async def create_user_or_get(
            self,
            username: str,
            user_id: int,
            **kwargs
    ) -> Tuple[User, bool]:
        return await self._class.get_or_create(
            username=username,
            user_id=user_id,
            **kwargs
        )

    async def get_user_or_none(self, user: Union[int, str]) -> User:
        if isinstance(user, int):
            user = await self._class.filter(user_id=user).first()
        else:
            user = await self._class.filter(username=user).first()
        return user

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass
