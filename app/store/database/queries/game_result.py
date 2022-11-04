from app.store.database.models import GameResult, User, Room


class GameResultDB:
    def __init__(self, _class: GameResult = GameResult):
        self._class = _class
    
    async def insert(
            self, room_id: int,
            recipient_id: int,
            sender_id: int
    ) -> GameResult:
        """ Create game result record"""
        room = await Room.filter(number=room_id).first()
        recipient = await User.filter(user_id=recipient_id).first()
        sender = await User.filter(user_id=sender_id).first()
        
        result = await self._class.create(
            room=room,
            recipient=recipient,
            sender=sender
        )
        return result
    
    async def get_recipient(self, room_id, user_id) -> User:
        """Get result for specific user"""
        results = await self._class.filter(
            room__number=room_id,
            sender__user_id=user_id
        ).first()
        return await results.recipient
