from typing import Tuple, Union

from app.store.database.models import User, Room

class UserDB:
    @staticmethod
    async def get_or_create(user_id, **kwargs
                            ) -> Tuple[User, bool]:
        """
        Get or create user's record in database
        :param user_id:
        :param kwargs:
        :return: [User Instance, Bool: Created - True, else False]
        """
        
        user, created = await User.get_or_create(
            user_id=user_id,
            defaults=kwargs
        )
        return user, created
    
    @staticmethod
    async def get_user_or_none(
            user: Union[int, str]
    ) -> Union[User, None]:
        """
        Get or do nothing
        :param user:
        :return: User instance or None
        """
        if isinstance(user, int):
            user = await User.filter(user_id=user).first()
        else:
            user = await User.filter(username=user).first()
        return user
    
    @staticmethod
    async def update_user(user_id: int, **kwargs) -> None:
        """
        Update any field of user instance
        """
        await User.filter(user_id=user_id).update(**kwargs)

    @staticmethod
    async def list_rooms_where_owner(user: User) -> list[Room]:
        """
        Get list of rooms where user is owner
        """
        user_rooms = await user.room_owner
        return user_rooms

    @staticmethod
    async def is_room_owner(user: User, room_number) -> bool:
        """
        Check if user is owner or room
        """
        user_rooms = await UserDB.list_rooms_where_owner(user)
        room = await Room.filter(number=room_number).first()
        return room in user_rooms
    
    @staticmethod
    async def disable_user(user_id: int) -> None:
        """
        Disable user
        """
        await User.filter(user_id=user_id).update(is_active=False)
    
    @staticmethod
    async def enable_user(user_id: int) -> None:
        """
        Enable user
        """
        await User.filter(user_id=user_id).update(is_active=True)
    
    @staticmethod
    async def delete_user(user_id: int) -> None:
        """
        delete user
        """
        user = await User.filter(user_id=user_id).first()
        await user.delete()
    
    @staticmethod
    async def get_list_all_users(order_by: str = 'user_id'):
        """get list all users"""
        result = await User.all().order_by(order_by)
        return result
    
    @staticmethod
    async def count_users():
        """get count all users"""
        result = await User.all().count()
        return result

    @staticmethod
    async def paginate(page: int, page_size: int) -> tuple:
        """Paginate user model"""
        items = await User.all().limit(page_size).offset((page - 1) * page_size)
        total_items = await User.all().count()
        return  items, total_items
