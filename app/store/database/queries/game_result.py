from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from app.store.database.models import GameResult, Room, User


class GameResultRepo:
    def __init__(self, session: Session):
        self.session = session
    
    async def insert(self, room_id: int, recipient_id: int, sender_id: int) -> GameResult:
        """Create game result record"""
        room = self.session.execute(select(Room).filter_by(number=room_id))
        recipient = self.session.execute(select(User).filter_by(user_id=recipient_id))
        sender = self.session.execute(select(User).filter_by(user_id=sender_id))
        
        room = room.scalars().first()
        recipient = recipient.scalars().first()
        sender = sender.scalars().first()
        
        result = GameResult(room_id=room.id, recipient_id=recipient.user_id, sender_id=sender.user_id)
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result
    
    async def get_recipient(self, room_id: int, user_id: int) -> User | None:
        """Get result for specific user"""
        results = self.session.execute(
            select(GameResult).filter_by(sender_id=user_id).join(Room)
            .filter_by(number=room_id)
            .options(selectinload(GameResult.recipient))
        )
        result = results.scalars().first()
        if not result:
            return None
        return result.recipient

    async def get_room_id_count(self, room_id: int) -> int:
        """Get the count of rows with the specified room_id"""
        result = self.session.query(GameResult).join(Room).filter(Room.number == room_id).count()
        return result
    
    async def get_sender(self, room_id: int, user_id: int) -> User | None:
        """Get result for specific user"""
        results = self.session.execute(
            select(GameResult).filter_by(recipient_id=user_id).join(Room)
            .filter_by(number=room_id)
            .options(selectinload(GameResult.sender))
        )
        result = results.scalars().first()
        if not result:
            return None
        return result.sender
