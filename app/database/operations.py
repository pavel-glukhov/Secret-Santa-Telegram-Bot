from datetime import datetime
from typing import ClassVar

from sqlalchemy.exc import SQLAlchemyError

from app.database.models import User, Room
from sqlalchemy import select
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
                          number: int,
                          owner_id: int,
                          budget: str) -> None:
        user = await UserDB(self.db_session).get_user(user_id=owner_id)
        room = Room(name=name,
                    number=number,
                    owner=user,
                    budget=budget)

        room.members = [user]
        self.db_session.add(room)

        try:
            await self.db_session.commit()
        except SQLAlchemyError as ex:
            logging.error(f"UserDB: 'crete user' method: {str(ex)}")

    async def update_room(self):
        pass

    async def add_member(self):
        pass

    async def remove_member(self):
        pass

    async def get_all_assigned_rooms(self, user_id):
        pass

    async def delete_room(self):
        pass

    async def change_owner(self):
        pass
