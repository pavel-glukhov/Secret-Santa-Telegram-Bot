import random
from typing import Type

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import load_config
from app.store.database.models import Room, User, WishRoom, rooms_users


class RoomRepo:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, name: str, owner_id: int, budget: str,
                     user_wish: str) -> Room:

        user = self.session.query(User).filter_by(user_id=owner_id).first()
        """
                Create a new room for The Secret Santa Game

                :param name: Name of the new room
                :param owner: Owner of the new room
                :param budget: Planned budget for the game
                :param user_wish: The wishes of the creator of the room
                :return: Room instance
                """
        if not user:
            raise ValueError(f"User with id {owner_id} does not exist.")

        unique_number = self._get_room_unique_number()

        room = Room(name=name, budget=budget, owner_id=owner_id, number=unique_number)
        self.session.add(room)
        self.session.commit()

        room.members.append(user)

        wish_room = WishRoom(wish=user_wish, user_id=owner_id, room_id=room.id)
        self.session.add(wish_room)
        self.session.commit()

        return room

    async def update(self, room_number: int, **kwargs) -> None:
        """
        Update data of a selected room

        :param room_number:  Number of game room
        :param kwargs:
        :return: None
        """

        room = self.session.query(Room).filter_by(number=room_number).first()
        if room:
            for key, value in kwargs.items():
                setattr(room, key, value)
            self.session.commit()

    async def add_member(self, user_id: int, room_number: int) -> bool:
        """
        Add new member to the room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: Bool
        """

        room = self.session.query(Room).filter_by(number=room_number).first()
        if not room:
            return False

        user = self.session.query(User).filter_by(user_id=user_id).first()
        room.members.append(user)
        self.session.commit()
        return True

    async def get_list_members(self, room_number: int):
        """
        Get all members of room

        :param room_number: Number of game room
        :return: Room instance
        """

        room = self.session.query(Room).filter_by(number=room_number).first()
        if room:
            return room.members
        return None

    async def remove_member(self, user_id: int, room_number: int) -> None:
        """
        Remove member from a room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: None
        """
        room = self.session.query(Room).filter_by(
            number=room_number).first()
        if not room:
            return None
        user = self.session.query(User).filter_by(
            user_id=user_id).join(rooms_users).filter(
            rooms_users.c.room_id == room.id).first()
        if not user:
            return None

        self.session.execute(
            delete(rooms_users).where(
                rooms_users.c.room_id == room.id,
                rooms_users.c.user_id == user_id
            )
        )
        self.session.execute(
            delete(WishRoom).where(
                WishRoom.room_id == room.id,
                WishRoom.user_id == user_id
            )
        )
        self.session.commit()

    async def is_exists(self, room_number: int) -> bool:
        return bool(self.session.query(Room).filter_by(
            number=room_number).first())

    async def is_member(self, user_id: int, room_number: int) -> bool:
        """
        Checking if user is member of room

        :param user_id: The telegram user_id of a user
        :param room_number:  Number of game room
        :return: Bool
        """
        room = self.session.query(Room).filter_by(
            number=room_number).first()
        if not room:
            return False

        for member in room.members:
            if member.user_id == user_id:
                return True

        return False

    async def get(self, room_number: int):
        """
        Get Room instance

        :param room_number: Number of game room
        :return: Room instance or None if not found
        """
        return self.session.query(Room).filter_by(
            number=room_number).first()

    async def change_owner(self, username: str, room_number: int):
        """
        Change owner of the room

        :param username: Telegram username of the new owner
        :param room_number: Room number of the room
        :return: User instance if owner changed successfully, else False
        """

        result = self.session.execute(
        select(Room, User).join(
            rooms_users, rooms_users.c.room_id == Room.id).join(
            User, User.user_id == rooms_users.c.user_id).filter(
            Room.number == room_number, User.username == username).first())

        if not result:
            return False

        room, user = result
        room.owner_id = user.user_id
        self.session.commit()
        return user

    async def get_all_users_of_room(self, user_id: int):
        """
        Get all rooms where the user is a member

        :param user_id: Telegram user ID of the user
        :return: List of Room instances
        """
        rooms = self.session.query(
            Room).join(
            rooms_users).filter(
            rooms_users.c.user_id == user_id
        ).all()
        return rooms

    async def delete(self, room_number: int):
        """
        Delete room by room number

        :param room_number: Room number to delete
        :return: True if deleted, False otherwise
        """
        room = self.session.query(Room).filter_by(
            number=room_number).first()
        if not room:
            return False

        self.session.delete(room)
        self.session.commit()
        return True

    async def is_owner(self, user_id, room_number: int):
        """
        Check if user is the owner of the room

        :param user_id: Telegram user ID of the user
        :param room_number: Room number to check
        :return: True if user is the owner, False otherwise
        """
        return self.session.query(
            self.session.query(Room).filter_by(
                number=room_number, owner_id=user_id
            ).exists()
        ).scalar()

    async def get_all_rooms(self):
        """
        Get all rooms

        :return: List of Room instances
        """
        return self.session.query(Room).all()

    async def count_rooms(self):
        """
        Count the total number of rooms

        :return: Total number of rooms
        """
        return self.session.query(Room).count()

    async def get_count_user_rooms(self, user_id):
        """
        Get the count of rooms owned by a user

        :param user_id: Telegram user ID of the user
        :return: Count of rooms owned by the user
        """
        return self.session.query(
            Room).filter_by(
            owner_id=user_id
        ).count()

    def _get_room_unique_number(self) -> int:

        """
        Non-public method for generate of individual room number.

        :return: int value
        """
        length = load_config().room.room_number_length
        min_number = int("1" + "0" * (length - 1))
        max_number = int("9" + "9" * (length - 1))

        rooms: list[Type[Room]] = self.session.query(Room).all()

        while True:
            number = random.randint(min_number, max_number)
            if number in [x.number for x in rooms]:
                continue
            else:
                return number
