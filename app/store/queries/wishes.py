from app.store.database.models import Wish


class WishRepo:
    async def get(self, user_id: int, room_id: int) -> Wish:
        result = await Wish.filter(
            room__number=room_id,
            user__user_id=user_id
        ).first()
        
        return result
    
    async def update_or_create(self, wish: str, user_id: int,
                               room_id: int) -> None:
        await Wish.update_or_create(
            user__user_id=user_id,
            room__number=room_id,
            defaults={
                'wish': wish,
            }
        )
    
    async def delete(self, room_id: int, user_id: int) -> None:
        wishes = await Wish.filter(
            room__number=room_id,
            user__user_id=user_id
        ).first()
        if wishes:
            await wishes.delete()
