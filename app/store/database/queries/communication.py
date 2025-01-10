from datetime import datetime

from sqlalchemy.orm import Session

from app.store.database.models import UsersMessages, Room


class CommunicationRepo:
    def __init__(self, session: Session):
        self.session = session
    
    async def insert(self, room: Room, recipient_id: int, sender_id: int, message: str) -> None:
        new_message = UsersMessages(
            recipient_id=recipient_id,
            sender_id=sender_id,
            room_id=room.id,
            message=message,
            sent_at=datetime.now()
        )
        
        self.session.add(new_message)
        self.session.commit()
