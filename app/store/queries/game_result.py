from app.store.database.models import GameResult, Room, User


class GameResultRepo:
    async def insert(self,
                     room_id: int,
                     recipient_id: int,
                     sender_id: int
                     ) -> GameResult:
        """ Create game result record"""
        room = await Room.filter(number=room_id).first()
        recipient = await User.filter(user_id=recipient_id).first()
        sender = await User.filter(user_id=sender_id).first()
        result = await GameResult.create(
            room=room,
            recipient=recipient,
            sender=sender
        )
        return result
    
    async def get_recipient(self,
                            room_id,
                            user_id
                            ) -> User | None:
        """Get result for specific user"""
        results = await GameResult.filter(
            room__number=room_id,
            sender__user_id=user_id
        ).first()
        if not results:
            return None
        return await results.recipient
    
    async def get_all_recipients(self,
                                 room_id,
                                 ) -> GameResult | None:
        """Get all results"""
        results = await GameResult.filter(
            room__number=room_id,
        ).all()
        if not results:
            return None
        return results
    
    async def get_sender(self,
                         room_id,
                         user_id
                         ) -> User:
        """Get result for specific user"""
        results = await GameResult.filter(
            room__number=room_id,
            recipient__user_id=user_id
        ).first()
        return await results.sender
