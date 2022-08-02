import random
from typing import Union, Tuple
from app.database.models import User, Room, Wish


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class

    async def create_user_or_get(self,
                                 username: str,
                                 user_id: int,
                                 **kwargs) -> Tuple[User, bool]:
        return await self._class.get_or_create(username=username,
                                               user_id=user_id,
                                               **kwargs)

    async def get_user_or_none(self, user_id: int) -> User:
        return await self._class.get_or_none(user_id=user_id)

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass


class WishDB:
    def __init__(self, _class: Wish = Wish):
        self._class = _class

    async def update_wish(self, wish: str,
                          user: User,
                          room: Room) -> Wish:
        pass


class RoomDB:
    def __init__(self, _class: Room = Room):
        self._class = _class

    async def create_room(self, name: str,
                          owner: int,
                          budget: str,
                          user_wish: str) -> Room:
        user = await UserDB().get_user_or_none(owner)

        unique_number = await self._get_room_unique_number()
        room = await self._class.create(name=name,
                                        budget=budget,
                                        owner=user,
                                        number=unique_number
                                        )

        await room.members.add(user)
        await Wish.create(wish=user_wish, user=user, room=room)

        return room

    async def update_room(self, room_number, **kwargs):
        await self._class.filter(number=room_number).update(**kwargs)

    async def add_member(self, user_id: int,
                         room_number: Union[int, str]) -> bool:

        user = await UserDB().get_user_or_none(user_id)
        room = await self._class.filter(number=room_number).first()

        if not room:
            return False

        await room.members.add(user)
        return True

    async def list_members(self, room_number: int) -> Room:
        room = await self._class.filter(number=room_number).first()
        return await room.members

    async def remove_member(self, user_id: int,
                            room_number: Union[int, str]) -> None:
        user = await UserDB().get_user_or_none(user_id)
        room = await self._class.filter(number=room_number).first()
        await room.members.remove(user)

    async def is_exists(self, room_number: Union[int, str]) -> bool:
        return await self._class.filter(number=room_number).exists()

    async def is_member(self, user_id,
                        room_number: Union[int, str]) -> bool:
        result = await self._class.filter(number=room_number,
                                          members__user_id=user_id).exists()
        return result

    async def get_room(self, room_number):
        return await self._class.filter(number=room_number).first()

    async def change_owner(self):
        pass

    async def get_joined_in_rooms(self, user_id: int) -> list[Room]:
        rooms = await self._class.filter(members__user_id=user_id)
        return rooms

    async def delete(self, room_number):
        room = await self._class.filter(number=room_number).first()
        await Wish.filter(room=room).delete()
        await room.delete()

    async def is_owner(self, user_id, room_number) -> bool:
        result = await self._class.filter(number=room_number,
                                          owner__user_id=user_id).exists()

        return result

    async def _get_room_unique_number(self) -> int:
        rooms: list[Room] = await self._class.all()
        while True:
            number: int = random.randint(100_000, 999_999)
            if number in [x.number for x in rooms]:
                continue
            else:
                return number
