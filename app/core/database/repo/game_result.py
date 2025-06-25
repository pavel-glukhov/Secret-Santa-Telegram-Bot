from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database.models import GameResult, Room, User


class GameResultRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, room_id: int,
                     recipient_id: int,
                     sender_id: int) -> GameResult:
        """Create game result record"""
        room_result = await self.session.execute(
            select(Room).filter_by(number=room_id)
        )
        room = room_result.scalars().first()

        recipient_result = await self.session.execute(
            select(User).filter_by(user_id=recipient_id)
        )
        recipient = recipient_result.scalars().first()

        sender_result = await self.session.execute(
            select(User).filter_by(user_id=sender_id)
        )
        sender = sender_result.scalars().first()

        result = GameResult(
            room_id=room.id,
            recipient_id=recipient.user_id,
            sender_id=sender.user_id
        )
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def get_recipient(self,
                            room_id: int,
                            user_id: int
                            ) -> User | None:
        """Get result for specific user"""
        results = await self.session.execute(
            select(GameResult)
            .filter_by(sender_id=user_id)
            .join(Room)
            .filter_by(number=room_id)
            .options(selectinload(GameResult.recipient))
        )
        result = results.scalars().first()
        if not result:
            return None
        return result.recipient

    async def get_room_id_count(self, room_id: int) -> int:
        """Get the count of rows with the specified room_id"""
        result = await self.session.execute(
            select(GameResult)
            .join(Room)
            .filter(Room.number == room_id)
        )
        return len(result.scalars().all())

    async def get_sender(self, room_id: int, user_id: int) -> User | None:
        """Get result for specific user"""
        results = await self.session.execute(
            select(GameResult)
            .filter_by(recipient_id=user_id)
            .join(Room)
            .filter_by(number=room_id)
            .options(selectinload(GameResult.sender))
        )
        result = results.scalars().first()
        if not result:
            return None
        return result.sender