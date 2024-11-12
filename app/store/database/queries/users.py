from typing import Tuple, Union

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, load_only

from app.store.database.models import Room, User


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    async def get_or_create(self, user_id, **kwargs) -> Tuple[User, bool]:
        """
        Get or create user's record in database
        :param user_id:
        :param kwargs:
        :return: [User Instance, Bool: Created - True, else False]
        """
        user = self.session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            instance = User(user_id=user_id, **kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance, True
        return user, False

    async def get_user_or_none(self, user: Union[int, str]) -> Union[User, None]:
        """
        Get or do nothing
        :param user:
        :return: User instance or None
        """
        if isinstance(user, int):
            result = self.session.execute(select(User).filter_by(user_id=user))
        else:
            result = self.session.execute(select(User).filter_by(username=user))
        user = result.scalars().first()
        return user

    async def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update any field of user instance
        """
        self.session.execute(update(User).filter_by(user_id=user_id).values(**kwargs))
        self.session.commit()

    async def list_rooms_where_owner(self, user: User) -> list[Room]:
        """
        Get list of rooms where user is owner
        """
        user_rooms = self.session.execute(select(Room).filter_by(owner_id=user.user_id))
        return user_rooms.scalars().all()

    async def is_room_owner(self, user: User, room_number) -> bool:
        """
        Check if user is owner of room
        """
        user_rooms = await self.list_rooms_where_owner(user)
        room = self.session.execute(select(Room).filter_by(number=room_number))
        room = room.scalars().first()
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
        user = self.session.get(User, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()

    async def get_list_all_users(self, order_by: str = 'user_id'):
        """Get list of all users"""
        result = self.session.execute(select(User).order_by(order_by))
        return result.scalars().all()

    async def count_users(self) -> int:
        """Get count of all users"""
        result = self.session.execute(select([func.count()]).select_from(User))
        return result.scalar()

    async def get_user_language(self, user_id):
        user = self.session.query(User).filter(User.user_id == user_id).first()
        if user is not None:
            return user.language
        return None
