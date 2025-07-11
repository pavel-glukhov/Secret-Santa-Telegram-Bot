from typing import Sequence, Tuple, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import Room, User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id, **kwargs) -> Tuple[User, bool]:
        """
        Get or create user's record in database
        :param user_id:
        :param kwargs:
        :return: [User Instance, Bool: Created - True, else False]
        """
        result = await self.session.execute(
            select(User).filter(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            instance = User(user_id=user_id, **kwargs)
            self.session.add(instance)
            await self.session.commit()
            return instance, True
        return user, False

    async def get_user_or_none(self,
                               user: Union[int, str]
                               ) -> Union[User, None]:
        """
        Get or do nothing
        :param user:
        :return: User instance or None
        """
        if isinstance(user, int):
            result = await self.session.execute(
                select(User).filter_by(user_id=user)
            )
        else:
            result = await self.session.execute(
                select(User).filter_by(username=user)
            )
        user = result.scalar_one_or_none()
        return user

    async def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update any field of user instance
        """
        await self.session.execute(
            update(User).filter_by(user_id=user_id).values(**kwargs)
        )
        await self.session.commit()

    async def list_rooms_where_owner(self, user: User) -> Sequence[Room]:
        """
        Get list of rooms where user is owner
        """
        result = await self.session.execute(
            select(Room).filter_by(owner_id=user.user_id)
        )
        return result.scalars().all()

    async def is_room_owner(self, user: User, room_number) -> bool:
        """
        Check if user is owner of room
        """
        user_rooms = await self.list_rooms_where_owner(user)
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        return room in user_rooms

    async def disable_user(self, user_id: int) -> None:
        """
        Disable user
        """
        await self.update_user(user_id, is_active=False)

    async def enable_user(self, user_id: int) -> None:
        """
        Enable user
        """
        await self.update_user(user_id, is_active=True)

    async def delete_user(self, user_id: int) -> None:
        """
        Delete user
        """
        user = await self.session.get(User, user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()

    async def get_user_language(self, user_id):
        """
        Get user's language
        """
        result = await self.session.execute(
            select(User).filter(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is not None:
            return user.language
        return None