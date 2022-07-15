import random
from datetime import datetime
from typing import ClassVar

from sqlalchemy.exc import SQLAlchemyError

from app.database.models import User, Room, Note
from sqlalchemy import select
from sqlalchemy.orm import load_only
import logging


class UserDB:
    def __init__(self, session):
        self.db_session = session

    async def create_user(self,
                          username: str,
                          user_id: int,
                          **kwargs) -> None:

        self.db_session.add(User(username=username,
                                 telegram_id=user_id,
                                 **kwargs))
        try:
            await self.db_session.commit()
        except SQLAlchemyError as ex:
            logging.error(f"UserDB: 'crete user' method: {str(ex)}")

    async def get_user(self, user_id: int) -> User:
        user = await self.db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        return user.scalars().one_or_none()

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass


class RoomDB:
    def __init__(self, session):
        self.db_session = session

    async def create_room(self, name: str,
                          owner_id: int,
                          budget: str,
                          user_note: str) -> Room:
        user = await UserDB(self.db_session).get_user(user_id=owner_id)
        room = Room(name=name,
                    number=await self._get_room_unique_number(),
                    owner=user,
                    budget=budget)
        note = Note(user=user, room=room, note=user_note)
        room.note = note
        room.members = [user]
        self.db_session.add(room)

        try:
            await self.db_session.commit()
        except SQLAlchemyError as ex:
            logging.error(f"UserDB: 'crete user' method: {str(ex)}")
        return room

    async def update_room(self):
        pass

    async def add_member(self):
        pass

    async def remove_member(self):
        pass

    async def get_room(self, number):
        room = await self.db_session.execute(
            select(Room).where(Room.number == number)
        )
        return room.scalars().one_or_none()

    async def get_all_number_rooms(self) -> list:
        room = await self.db_session.execute(
            select(Room.members))
        return room.scalars().all()

    async def get_joined_rooms(self, user_id: int):

        rooms = await self.db_session.execute(
            select(
                Room).where(
                Room.members.any(
                    User.telegram_id == user_id)
            )
        )
        return rooms.scalars().all()

    async def delete_room(self):
        pass

    async def change_owner(self):
        pass

    async def _get_room_unique_number(self):
        numbers_rooms = await self.get_all_number_rooms()
        while True:
            number = random.randint(100_000, 999_999)
            if number in numbers_rooms:
                continue
            else:
                return number
