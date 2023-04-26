import random
from typing import Union

from app.config import load_config
from app.store.database.models import Room, User, Wish
from app.store.database.queries.users import UserDB


class RoomDB:

    @staticmethod
    async def create(name: str,
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

        unique_number = await RoomDB._get_room_unique_number()
        room = await Room.create(
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

    @staticmethod
    async def update(room_number: int, **kwargs) -> None:
        """
        Update data of a selected room

        :param room_number:  Number of game room
        :param kwargs:
        :return: None
        """
        await Room.filter(number=room_number).update(**kwargs)

    @staticmethod
    async def add_member(user_id: int,
                         room_number: int) -> bool:
        """
        Add new member to the room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: Bool
        """

        user = await UserDB().get_user_or_none(user_id)
        room = await Room.filter(number=room_number).first()

        if not room:
            return False

        await room.members.add(user)
        return True

    @staticmethod
    async def get_list_members(room_number: int) -> Room:
        """
        Get all members of room

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await Room.filter(number=room_number).first()
        return await room.members

    @staticmethod
    async def remove_member(user_id: int,
                            room_number: int) -> None:
        """
        Remove member from a room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: None
        """
        user = await UserDB().get_user_or_none(user_id)
        room = await Room.filter(number=room_number).first()
        await room.members.remove(user)

    @staticmethod
    async def is_exists(room_number: int) -> bool:
        result = await Room.filter(number=room_number).exists()
        return result

    @staticmethod
    async def is_member(user_id, room_number: int) -> bool:
        """
        Checking if user is member of room

        :param user_id: The telegram user_id of a user
        :param room_number:  Number of game room
        :return: Bool
        """
        result = await Room.filter(
            number=room_number,
            members__user_id=user_id
        ).exists()
        return result

    @staticmethod
    async def get(room_number: int) -> Room:
        """
        Get Room instance

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await Room.filter(number=room_number).first()
        return room

    @staticmethod
    async def change_owner(username: str,
                           room_number: int) -> Union[User, bool]:
        """
        Change of owner in the room

        :param username: Telegram username of a user
        :param room_number: Room number of the Santa Game
        :return: User instance or False if the user is not found.
        """
        user = await UserDB().get_user_or_none(username)
        room = await Room.filter(number=room_number).first()
        room_members = await room.members

        if user in room_members:
            await Room.filter(number=room_number).update(owner=user)
            return user
        return False

    @staticmethod
    async def get_all_users_of_room(user_id: int) -> list[Room]:
        """
        Get the entire list of the user's rooms in which he is a member

        :param user_id: The telegram user_id of a user
        :return: List of Room instances
        """
        rooms = await Room.filter(members__user_id=user_id)
        return rooms

    @staticmethod
    async def delete(room_number: int) -> bool:
        """
        Delete room

        :param room_number:
        :return: Return True if is deleted else False
        """
        room = await Room.filter(number=room_number).first()
        if not room:
            return False

        await Wish.filter(room=room).delete()
        await room.delete()
        return True

    @staticmethod
    async def is_owner(user_id, room_number: int) -> bool:
        """
        Checking if user is owner of room

        :param user_id: Telegram user ID of user
        :param room_number: Room number for checking on the owner
        :return: True or False
        """
        result = await Room.filter(
            number=room_number,
            owner__user_id=user_id
        ).exists()

        return result

    @staticmethod
    async def _get_room_unique_number() -> int:

        """
        Non-public method for generate of individual room number.

        :return: int value
        """
        length = load_config().room.room_number_length
        min_number = int("1" + "0" * (length - 1))
        max_number = int("9" + "9" * (length - 1))

        rooms: list[Room] = await Room.all()

        while True:
            number = random.randint(min_number, max_number)
            if number in [x.number for x in rooms]:
                continue
            else:
                return number
