import random
from typing import Union

from app.config import load_config
from app.store.database.models import Room, User, WishRoom
from app.store.queries.users import UserRepo


class RoomRepo:
    
    async def create(self, name: str, owner: int, budget: str,
                     user_wish: str) -> Room:
        """
        Create a new room for The Secret Santa Game

        :param name: Name of the new room
        :param owner: Owner of the new room
        :param budget: Planned budget for the game
        :param user_wish: The wishes of the creator of the room
        :return: Room instance
        """
        user = await UserRepo().get_user_or_none(owner)
        unique_number = await self._get_room_unique_number()
        room = await Room.create(
            name=name,
            budget=budget,
            owner=user,
            number=unique_number
        )
        
        await room.members.add(user)
        await WishRoom.create(wish=user_wish, user=user, room=room)
        
        return room
    
    async def update(self, room_number: int, **kwargs) -> None:
        """
        Update data of a selected room

        :param room_number:  Number of game room
        :param kwargs:
        :return: None
        """
        await Room.filter(number=room_number).update(**kwargs)
    
    async def add_member(self, user_id: int, room_number: int) -> bool:
        """
        Add new member to the room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: Bool
        """
        user = await UserRepo().get_user_or_none(user_id)
        room = await Room.filter(number=room_number).first()
        
        if not room:
            return False
        
        await room.members.add(user)
        return True
    
    async def get_list_members(self, room_number: int) -> Room:
        """
        Get all members of room

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await Room.filter(number=room_number).first()
        return await room.members.order_by('user_id')
    
    async def remove_member(self, user_id: int, room_number: int) -> None:
        """
        Remove member from a room

        :param user_id: The telegram user_id of a user
        :param room_number: Number of game room
        :return: None
        """
        user = await UserRepo().get_user_or_none(user_id)
        room = await Room.filter(number=room_number).first()
        await room.members.remove(user)
        await WishRoom.filter(user=user, room=room).delete()

    async def is_exists(self, room_number: int) -> bool:
        result = await Room.filter(number=room_number).exists()
        return result
    
    async def is_member(self, user_id, room_number: int) -> bool:
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
    
    async def get(self, room_number: int) -> Room:
        """
        Get Room instance

        :param room_number: Number of game room
        :return: Room instance
        """
        room = await Room.filter(number=room_number).first()
        return room
    
    async def change_owner(self, username: str,
                           room_number: int) -> Union[User, bool]:
        """
        Change of owner in the room

        :param username: Telegram username of a user
        :param room_number: Room number of the Santa Game
        :return: User instance or False if the user is not found.
        """
        user = await UserRepo().get_user_or_none(username)
        room = await Room.filter(number=room_number).first()
        room_members = await room.members
        
        if user in room_members:
            await Room.filter(number=room_number).update(owner=user)
            return user
        return False
    
    async def get_all_users_of_room(self, user_id: int) -> list[Room]:
        """
        Get the entire list of the user's rooms in which he is a member

        :param user_id: The telegram user_id of a user
        :return: List of Room instances
        """
        rooms = await Room.filter(
            members__user_id=user_id).prefetch_related('owner')
        return rooms
    
    async def delete(self, room_number: int) -> bool:
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
    
    async def is_owner(self, user_id, room_number: int) -> bool:
        """
        Checking if user is owner of specified room

        :param user_id: Telegram user ID of user
        :param room_number: Room number for checking on the owner
        :return: True or False
        """
        result = await Room.filter(
            number=room_number,
            owner__user_id=user_id
        ).exists()
        
        return result
    
    async def get_all_rooms(self):
        """return list of all rooms"""
        result = await Room.all().prefetch_related('owner')
        return result
    
    async def count_rooms(self):
        """return count of all rooms"""
        result = await Room.all().count()
        return result
    
    async def get_count_user_rooms(self, user_id) -> int:
        """
        Get count user's rooms
        """
        result = await Room.filter(owner__user_id=user_id).count()
        
        return result
    
    async def _get_room_unique_number(self) -> int:
        
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
