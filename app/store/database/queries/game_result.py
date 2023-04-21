from app.store.database.models import GameResult, Room, User


class GameResultDB:

    @staticmethod
    async def insert(
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

    @staticmethod
    async def get_recipient(
            room_id,
            user_id
    ) -> User:
        """Get result for specific user"""
        results = await GameResult.filter(
            room__number=room_id,
            sender__user_id=user_id
        ).first()
        return await results.recipient

    @staticmethod
    async def get_sender(
            room_id,
            user_id
    ) -> User:
        """Get result for specific user"""
        results = await GameResult.filter(
            room__number=room_id,
            recipient__user_id=user_id
        ).first()
        return await results.sender