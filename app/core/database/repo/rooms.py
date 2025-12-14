import random
from typing import Any, List, Optional, Sequence

from sqlalchemy import Row, RowMapping, delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from app.core.config.app_config import load_config
from app.core.database.models import Room, User, WishRoom, rooms_users
from app.core.database.repo.wishes import WishRepo


class RoomRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, owner_id: int, budget: str,
                     user_wish: str) -> Room:
        """
        Create a new room for The Secret Santa Game
        :param name: Name of the new room
        :param owner_id: ID of the owner of the new room
        :param budget: Planned budget for the game
        :param user_wish: The wishes of the creator of the room
        :return: Room instance
        """
        result = await self.session.execute(
            select(User).filter_by(user_id=owner_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with id {owner_id} does not exist.")

        rooms_result = await (self.session.execute(select(Room.number)))
        list_of_rooms = rooms_result.scalars().all()
        unique_number = await self._get_room_unique_number(list_of_rooms)

        room = Room(name=name, budget=budget, owner_id=owner_id, number=unique_number)
        self.session.add(room)
        await self.session.flush()

        await self.session.execute(
            insert(rooms_users).values(room_id=room.id, user_id=owner_id)
        )

        wish_room = WishRoom(wish=user_wish, user_id=owner_id, room_id=room.id)
        self.session.add(wish_room)
        await self.session.commit()

        return room

    async def update(self, room_number: int, **kwargs) -> None:
        """
        Update data of a selected room
        :param room_number: Number of game room
        :param kwargs: Fields to update
        :return: None
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        if room:
            for key, value in kwargs.items():
                setattr(room, key, value)
            await self.session.commit()

    async def add_member(self, user_id: int, room_number: int, user_wish: str) -> bool:
        """
        Add new member to the room
        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :param user_wish: The wishes of the member of the room
        :return: Bool
        """
        result = await self.session.execute(
            select(Room).filter_by(number=int(room_number))
        )
        room = result.scalar_one_or_none()
        if not room:
            return False

        result = await self.session.execute(
            select(User).filter_by(user_id=int(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        result = await self.session.execute(
            select(rooms_users).filter_by(room_id=room.id, user_id=int(user_id))
        )
        if result.scalar_one_or_none():
            return True

        await self.session.execute(
            insert(rooms_users).values(room_id=room.id, user_id=int(user_id))
        )
        await WishRepo(self.session).create_or_update_wish_for_room(
            user_id=user_id,
            room_id=room.id,
            wish=user_wish
        )

        await self.session.commit()
        return True

    async def get_list_members(self, room_number: int) -> Optional[List[User]]:
        """
        Get all members of room
        :param room_number: Number of game room
        :return: List of User instances or None
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        if not room:
            return None

        result = await self.session.execute(
            select(User)
            .join(rooms_users, rooms_users.c.user_id == User.user_id)
            .filter(rooms_users.c.room_id == room.id)
        )
        return result.scalars().all()

    async def remove_member(self, user_id: int, room_number: int) -> None:
        """
        Remove member from a room
        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: None
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        if not room:
            return

        await self.session.execute(
            delete(rooms_users).where(
                rooms_users.c.room_id == room.id,
                rooms_users.c.user_id == user_id
            )
        )
        await self.session.execute(
            delete(WishRoom).where(
                WishRoom.room_id == room.id,
                WishRoom.user_id == user_id
            )
        )
        await self.session.commit()

    async def is_exists(self, room_number: int) -> bool:
        """
        Check if room exists
        :param room_number: Number of game room
        :return: Bool
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        return bool(result.scalar_one_or_none())

    async def is_member(self, user_id: int, room_number: int) -> bool:
        """
        Checking if user is member of room
        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: Bool
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        if not room:
            return False

        result = await self.session.execute(
            select(rooms_users).filter_by(room_id=room.id, user_id=user_id)
        )
        return bool(result.scalar_one_or_none())

    async def get(self, room_number: int) -> Optional[Room]:
        """
        Get Room instance
        :param room_number: Number of game room.
        :return: Room instance or None if not found.
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        return result.scalar_one_or_none()

    async def change_owner(self, username: str, room_number: int) -> User | bool:
        """
        Change owner of the room.
        :param username: Telegram username of the new owner.
        :param room_number: Room number of the room.
        :return: User instance if owner changed successfully, else False.
        """
        result = await self.session.execute(
            select(Room, User)
            .join(rooms_users, rooms_users.c.room_id == Room.id)
            .join(User, User.user_id == rooms_users.c.user_id)
            .filter(Room.number == room_number, User.username == username)
        )
        row = result.first()
        if not row:
            return False

        room, user = row
        room.owner_id = user.user_id
        await self.session.commit()
        return user

    async def get_all_users_of_room(self, user_id: int) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Get all rooms where the user is a member
        :param user_id: Telegram user ID of the user
        :return: List of Room instances
        """
        result = await self.session.execute(
            select(Room)
            .join(rooms_users)
            .filter(rooms_users.c.user_id == user_id)
        )
        return result.scalars().all()

    async def delete(self, room_number: int) -> bool:
        """
        Delete room by room number.
        :param room_number: Room number to delete.
        :return: True if deleted, False otherwise.
        """
        result = await self.session.execute(
            select(Room).filter_by(number=room_number)
        )
        room = result.scalar_one_or_none()
        if not room:
            return False

        await self.session.delete(room)
        await self.session.commit()
        return True

    async def is_owner(self, user_id: int, room_number: int) -> bool:
        """
        Check if user is the owner of the room
        :param user_id: Telegram user ID of the user
        :param room_number: Room number to check
        :return: True if user is the owner, False otherwise
        """
        result = await self.session.execute(
            select(exists().where(
                Room.number == room_number,
                Room.owner_id == user_id
            ))
        )
        return result.scalar()

    async def get_all_rooms(self) -> Sequence[Room]:
        """
        Get all rooms
        :return: List of Room instances
        """
        result = await self.session.execute(select(Room))
        return result.scalars().all()

    async def count_rooms(self) -> int:
        """
        Count the total number of rooms
        :return: Total number of rooms
        """
        result = await self.session.execute(
            select(func.count()).select_from(Room)
        )
        return result.scalar()

    async def get_count_user_rooms(self, user_id: int) -> int:
        """
        Get the count of rooms owned by a user
        :param user_id: Telegram user ID of the user
        :return: Count of rooms owned by the user
        """
        result = await self.session.execute(
            select(func.count()).select_from(Room).filter_by(owner_id=user_id)
        )
        return result.scalar()

    @staticmethod
    async def _get_room_unique_number(list_of_rooms) -> int:
        length = load_config().room.room_number_length

        min_number = 10 ** (length - 1)
        max_number = 10 ** length - 1

        used_numbers = set(list_of_rooms)

        if len(used_numbers) >= max_number - min_number + 1:
            raise ValueError("There are no unique room numbers available. The pool of numbers has ended."
                             "Solution: it is necessary to expand the range.")

        while True:
            number = random.randint(min_number, max_number)
            if number not in used_numbers:
                return number
