import random
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.database.models import User, Room, Note, RoomUser
from sqlalchemy import select, delete, insert
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
            await self.db_session.flush()
        except SQLAlchemyError as ex:
            self.db_session.rollback()
            logging.error(f"UserDB: 'crete user' method: {str(ex)}")

    async def get_user_or_none(self, user_id: int) -> User:
        user = await self.db_session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        return user.scalars().one_or_none()

    async def create_if_not_exist(self,
                                  username: str,
                                  user_id: int,
                                  first_name: str,
                                  last_name: str) -> None:
        user = await self.get_user_or_none(user_id=user_id)
        if not user:
            await self.create_user(
                username=username,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name
            )

    async def update_user(self):
        pass

    async def activate_user(self):
        pass

    async def deactivate_user(self):
        pass


class NoteDB:
    def __init__(self, session):
        self.db_session = session

    async def update_note(self, note: str,
                          user: User,
                          room: Room) -> Note:
        pass


class RoomDB:
    def __init__(self, session):
        self.db_session = session

    async def create_room(self, name: str,
                          owner: int,
                          budget: str,
                          user_note: str) -> Room:

        user = await UserDB(self.db_session).get_user_or_none(
            user_id=owner
        )

        room_number = await self._get_room_unique_number()

        room = Room(name=name,
                    number=room_number,
                    owner=user,
                    budget=budget)
        note = Note(note=user_note, room=room, user=user)
        room.members = [user]
        self.db_session.add(room)
        self.db_session.add(note)

        try:
            await self.db_session.flush()
        except SQLAlchemyError as ex:
            self.db_session.rollback()
            logging.error(f"RoomDB: 'crete room' method: {str(ex)}")
        return room

    async def update_room(self, room_number):

        pass

    async def add_member(self, user, room_number):
        user = await self.db_session.execute(select(
            User).where(User.telegram_id == user))

        room = await self.db_session.execute(select(
            Room).where(Room.number == room_number).options(selectinload(Room.members)))

        us_result = user.scalars().first()
        ro_result = room.scalars().one_or_none()

        if ro_result:
            if us_result not in ro_result.members:
                room_user = RoomUser(user_id=us_result.id, room_id=ro_result.id)
                self.db_session.add(room_user)

                try:
                    await self.db_session.flush()
                except SQLAlchemyError as ex:
                    self.db_session.rollback()
                    logging.error(f"RoomDB: 'add_member' method: {str(ex)}")

                return True
        return False

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

    async def get_joined_in_rooms(self, user_id: int):
        rooms = await self.db_session.execute(
            select(
                Room).where(
                Room.members.any(
                    User.telegram_id == user_id)
            )
        )
        return rooms.scalars().all()

    async def delete_room(self, room_number):
        await self.db_session.execute(delete(Room).where(
            Room.number == room_number))

    async def change_owner(self):
        pass

    async def is_owner(self, user_id):
        room = await self.db_session.execute(
            select(Room.owner).where(Room.owner.telegram_id == user_id)
        )
        return room.scalars().one_or_none()

    async def _get_room_unique_number(self):
        numbers_rooms = await self.get_all_number_rooms()
        while True:
            number = random.randint(100_000, 999_999)
            if number in numbers_rooms:
                continue
            else:
                return number
