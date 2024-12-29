from sqlalchemy.orm import Session

from app.store.database.models import Room, User, WishRoom


class WishRepo:
    def __init__(self, session: Session):
        self.session = session
    
    async def get(self, user_id: int, room_id: int) -> WishRoom | None:
        """
        Get user's wish for a specific room

        :param user_id: Telegram user ID of the user
        :param room_id: Room number
        :return: WishRoom instance or None if not found
        """
        user = self.session.query(User).filter_by(user_id=user_id).first()
        room = self.session.query(Room).filter_by(number=room_id).first()
        
        if user and room:
            user_wish_in_room = self.session.query(
                WishRoom).filter_by(user=user, room=room).first()
            return user_wish_in_room.wish
        
        return None

    async def create_or_update_wish_for_room(self,
                                             wish: str,
                                             user_id: int,
                                             room_id: int) -> None:
        """
        Create or update a wish for a specific room

        :param wish: Wish text
        :param user_id: Telegram user ID of the user
        :param room_id: Room number
        """
        user = self.session.query(User).filter_by(user_id=user_id).first()
        room = self.session.query(Room).filter_by(number=room_id).first()
    
        if user and room:
            existing_wish = self.session.query(
                WishRoom).filter_by(
                user_id=user.user_id, room_id=room.id
            ).first()
        
            if existing_wish:
                existing_wish.wish = wish
            else:
                new_wish = WishRoom(user=user,
                                    room=room,
                                    wish=wish)
                self.session.add(new_wish)
        
            self.session.commit()
    
    async def delete(self, user_id: int, room_id: int) -> None:
        """
        Delete user's wish for a specific room

        :param user_id: Telegram user ID of the user
        :param room_id: Room number
        """
        user_wish_in_room = self.session.query(
            WishRoom).filter_by(
            user_id=user_id, room_id=room_id
        ).first()
        
        if user_wish_in_room:
            self.session.delete(user_wish_in_room)
            self.session.commit()
