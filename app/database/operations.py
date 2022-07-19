import datetime
import random
import typing
from app.database.models import User, Room, Note


class UserDB:
    def __init__(self, _class: User = User):
        self._class = _class

    async def create_user_or_get(self,
                                 username: str,
                                 user_id: int,
                                 **kwargs) -> typing.Tuple[User, bool]:
        return await self._class.get_or_create(username=username,
                                               telegram_id=user_id,
                                               **kwargs)

    async def get_user_or_none(self, user_id: int) -> User:
        return await self._class.get_or_none(telegram_id=user_id)

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass


class NoteDB:
    def __init__(self, _class: Note = Note):
        self._class = _class

    async def update_note(self, note: str,
                          user: User,
                          room: Room) -> Note:
        pass


class RoomDB:
    def __init__(self, _class: Room = Room):
        self._class = _class

    async def create_room(self, name: str,
                          owner: int,
                          budget: str,
                          user_note: str) -> Room:
        user = await UserDB().get_user_or_none(owner)

        unique_number = await self._get_room_unique_number()
        room = await self._class.create(name=name,
                                        budget=budget,
                                        owner=user,
                                        number=unique_number
                                        )

        await room.members.add(user)
        await Note.create(note=user_note, user=user, room=room)

        return room

    async def update_room(self, room_number):
        pass

    async def add_member(self, user_id: int, room_number: int):

        user = await UserDB().get_user_or_none(user_id)
        room = await self._class.filter(number=room_number).first()
        if not room:
            return False

        await room.members.add(user)
        return True

    async def remove_member(self):
        pass

    async def get_room(self, number):
        pass

    async def get_joined_in_rooms(self, user_id: int) -> list[Room]:
        user = await UserDB().get_user_or_none(user_id)
        rooms = await self._class.filter(members=user)
        return rooms

    async def delete_room(self, room_number):
        room = await self._class.filter(number=room_number).first()
        await Note.filter(room=room).delete()
        await room.delete()

    async def change_owner(self):
        pass

    async def is_owner(self, user_id):
        pass

    async def _get_room_unique_number(self) -> int:
        rooms: list[Room] = await self._class.all()
        while True:
            number: int = random.randint(100_000, 999_999)
            if number in [x.number for x in rooms]:
                continue
            else:
                return number
