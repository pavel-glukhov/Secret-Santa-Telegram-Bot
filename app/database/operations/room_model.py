import random
from typing import Union

from app.config import config
from app.database.models import Room, Wish, User
from app.database.operations.user_model import UserDB


class RoomDB:
    def __init__(self, _class: Room = Room):
        self._class = _class

    async def create_room(self, name: str,
                          owner: int,
                          budget: str,
                          user_wish: str) -> Room:
        """
        Create a new room for The Secret Santa Game

        :param name: Name of the new room
        :param owner: Owner of the new room
        :param budget: Planned budget for the game
        :param user_wish: The wishes of the creator of the room
        :return: Room instance
        """
        user = await UserDB().get_user_or_none(owner)

        unique_number = await self._get_room_unique_number()
        room = await self._class.create(
            name=name,
            budget=budget,
            owner=user,
            number=unique_number
        )

        await room.members.add(user)
        await Wish.create(
            wish=user_wish,
            user=user, room=room
        )

        return room

    async def update_room(self, room_number: int, **kwargs) -> None:
        """
        Update data of a selected room

        :param room_number:  Number of game room
        :param kwargs:
        :return: None
        """
        await self._class.filter(number=room_number).update(**kwargs)

    async def add_member(self, user_id: int,
                         room_number: int) -> bool:
        """
        Add new member to the room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: Bool
        """

        user = await UserDB().get_user_or_none(user_id)
        room = await self._class.filter(number=room_number).first()

        if not room:
            return False

        await room.members.add(user)
        return True

    async def list_members(self, room_number: int) -> Room:
        """
        Get all members of room

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await self._class.filter(number=room_number).first()
        return await room.members

    async def remove_member(self, user_id: int,
                            room_number: int) -> None:
        """
        Remove member from a room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: None
        """
        user = await UserDB().get_user_or_none(user_id)
        room = await self._class.filter(number=room_number).first()
        await room.members.remove(user)

    async def is_exists(self, room_number: int) -> bool:
        result = await self._class.filter(number=room_number).exists()
        return result

    async def is_member(self, user_id, room_number: int) -> bool:
        """
        Checking if user is member of room

        :param user_id: The telegram user_id of a user
        :param room_number:  Number of game room
        :return: Bool
        """
        result = await self._class.filter(
            number=room_number,
            members__user_id=user_id
        ).exists()
        return result

    async def get_room(self, room_number: int) -> Room:
        """
        Get Room instance

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await self._class.filter(number=room_number).first()
        return room

    async def change_owner(self, username: str,
                           room_number: int) -> Union[User, bool]:
        """
        Change of owner in the room

        :param username: Telegram username of a user
        :param room_number: Room number of the Santa Game
        :return: User instance or False if the user is not found.
        """
        user = await UserDB().get_user_or_none(username)
        room = await self._class.filter(number=room_number).first()
        room_members = await room.members

        if user in room_members:
            await self._class.filter(number=room_number).update(owner=user)
            return user
        return False

    async def get_all_user_rooms(self, user_id: int) -> list[Room]:
        """
        Get the entire list of the user's rooms in which he is a member

        :param user_id: The telegram user_id of a user
        :return: List of Room instances
        """
        rooms = await self._class.filter(members__user_id=user_id)
        return rooms

    async def delete(self, room_number: int) -> bool:
        """
        Delete room

        :param room_number:
        :return: Return True if is deleted else False
        """
        room = await self._class.filter(number=room_number).first()
        if not room:
            return False

        await Wish.filter(room=room).delete()
        await room.delete()
        return True

    async def is_owner(self, user_id, room_number: int) -> bool:
        """
        Checking if user is owner of room

        :param user_id: Telegram user ID of user
        :param room_number: Room number for checking on the owner
        :return: True or False
        """
        result = await self._class.filter(
            number=room_number,
            owner__user_id=user_id
        ).exists()

        return result

    async def _get_room_unique_number(self) -> int:

        """
        Non-public method for generate of individual room number.

        :return: int value
        """
        length = config.room.room_number_length
        min_number = int("1" + "0" * (length - 1))
        max_number = int("9" + "9" * (length - 1))

        rooms: list[Room] = await self._class.all()

        while True:
            number = random.randint(min_number, max_number)
            if number in [x.number for x in rooms]:
                continue
            else:
                return number
