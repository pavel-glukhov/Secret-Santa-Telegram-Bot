from typing import Tuple, Union

from app.store.database.models import User


class UserDB:
    @staticmethod
    async def get_or_create(user_id, **kwargs
                            ) -> Tuple[User, bool]:
        """
        Get or create user's record in database
        :param user_id:
        :param kwargs:
        :return: [User Instance, Bool: Created - True, else False]
        """

        user, created = await User.get_or_create(
            user_id=user_id,
            defaults=kwargs
        )
        return user, created

    @staticmethod
    async def get_user_or_none(
            user: Union[int, str]
    ) -> Union[User, None]:
        """
        Get or do nothing
        :param user:
        :return: User instance or None
        """
        if isinstance(user, int):
            user = await User.filter(user_id=user).first()
        else:
            user = await User.filter(username=user).first()
        return user

    @staticmethod
    async def update_user(user_id: int, **kwargs: str) -> None:
        """
        Update any field of user instance
        """
        await User.filter(user_id=user_id).update(**kwargs)

    @staticmethod
    async def disable_user(user_id: int) -> None:
        """
        Disable user
        """
        await User.filter(user_id=user_id).update(is_active=False)

    @staticmethod
    async def enable_user(user_id: int) -> None:
        """
        Enable user
        """
        await User.filter(user_id=user_id).update(is_active=True)
