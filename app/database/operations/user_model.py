from typing import Tuple, Union

from app.database.models import User


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class

    async def get_or_create(self, user_id, **kwargs
                            ) -> Tuple[User, bool]:

        user, created = await self._class.get_or_create(
            user_id=user_id,
            defaults=kwargs
        )
        return user, created


    async def get_user_or_none(self, user: Union[int, str]) -> User:
        if isinstance(user, int):
            user = await self._class.filter(user_id=user).first()
        else:
            user = await self._class.filter(username=user).first()
        return user

    async def update_user(self, user_id: int, **kwargs: str) -> None:
        await self._class.filter(user_id=user_id).update(**kwargs)
