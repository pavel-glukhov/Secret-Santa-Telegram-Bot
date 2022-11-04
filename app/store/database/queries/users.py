from typing import Tuple, Union

from app.store.database.models import User


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class
    
    async def get_or_create(self, user_id, **kwargs
                            ) -> Tuple[User, bool]:
        """
        Get or create user's record in database
        :param user_id:
        :param kwargs:
        :return: [User Instance, Bool: Created - True, else False]
        """
        
        user, created = await self._class.get_or_create(
            user_id=user_id,
            defaults=kwargs
        )
        return user, created
    
    async def get_user_or_none(
            self, user: Union[int, str]
    ) -> Union[User, None]:
        """
        Get or do nothing
        :param user:
        :return: User instance or None
        """
        if isinstance(user, int):
            user = await self._class.filter(user_id=user).first()
        else:
            user = await self._class.filter(username=user).first()
        return user
    
    async def update_user(self, user_id: int, **kwargs: str) -> None:
        """
        Update any field of user instance
        """
        await self._class.filter(user_id=user_id).update(**kwargs)
    
    async def disable_user(self, user_id: int) -> None:
        """
        Disable user
        """
        await self._class.filter(user_id=user_id).update(is_active=False)
    
    async def enable_user(self, user_id: int) -> None:
        """
        Enable user
        """
        await self._class.filter(user_id=user_id).update(is_active=True)
