from app.database.models import Wish

class WishDB:
    def __init__(self, _class: Wish = Wish):
        self._class = _class

    async def get_wishes(self, room_id: int, user_id: int) -> Wish:
        result = await self._class.filter(room__number=room_id,
                                          user__user_id=user_id).first()
        return result

    async def update_or_create(self, wish: str,
                               user_id: int,
                               room_id: int) -> None:
        await self._class.update_or_create(user__user_id=user_id,
                                           room__number=room_id,
                                           defaults={
                                               'wish': wish,
                                           }
                                           )

    async def delete_wishes(self, room_id: int, user_id: int) -> None:
        wishes = await self._class.filter(room__number=room_id,
                                          user__user_id=user_id).first()
        if wishes:
            await wishes.delete()

