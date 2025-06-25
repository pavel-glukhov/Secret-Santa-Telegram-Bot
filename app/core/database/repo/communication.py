from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import Room, UsersMessages


class CommunicationRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, room: Room,
                     recipient_id: int,
                     sender_id: int,
                     message: str) -> None:
        new_message = UsersMessages(
            recipient_id=recipient_id,
            sender_id=sender_id,
            room_id=room.id,
            message=message,
            sent_at=datetime.now()
        )

        self.session.add(new_message)
        await self.session.commit()