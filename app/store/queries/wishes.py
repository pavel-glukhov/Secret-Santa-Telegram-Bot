from app.store.database.models import Room, User, WishRoom
from app.store.queries.users import UserRepo


class WishRepo:
    # async def get(self, user_id: int, room_id: int) -> Wish:
    #     result = await Wish.filter(
    #         room__number=room_id,
    #         user__user_id=user_id
    #     ).first()
    #
    #     return result
    
    async def get(self, user_id: int,
                  room_id: int) -> WishRoom | None:
        user = await User.get_or_none(user_id=user_id)
        room = await Room.get_or_none(number=room_id)
        
        if user and room:
            user_wish_in_room = await WishRoom.filter(user=user,
                                                      room=room).first()
            return user_wish_in_room
        return None
    
    async def create_wish_for_room(self, wish: str, user_id: int,
                                   room_id: int) -> None:
        user = await UserRepo().get_user_or_none(user_id)
        room = await Room.filter(number=room_id).first()
        await WishRoom.create(
            user=user,
            room=room,
            wish=wish
        )
    
    async def delete(self, user_id: int,
                     room_id: int) -> None:
        user_wish_in_room = await WishRoom.filter(user__user_id=user_id,
                                                  room__number=room_id).first()
        
        if user_wish_in_room:
            await user_wish_in_room.delete()
