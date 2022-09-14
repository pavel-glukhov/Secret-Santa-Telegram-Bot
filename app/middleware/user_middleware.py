from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

# TODO Написать мидлваре на регистрацию пользователя.
# class UserMiddleware(BaseMiddleware):
#
#     @staticmethod
#     async def get(data: dict, user: types.User, message: types.Message):
#         user = await User.get(user.id)
#
#         if user is None:
#             user = await User.create(user_id=user.id)
#
#         if user.is_blocked:
#             # Send message and cancel handler
#             await message.answer('Вы заблокированы!')
#             raise CancelHandler()
#
#         # Save user
#         data["user"] = user
#
#     async def on_pre_process_message(self, message: types.Message, data: dict):
#         await self.get(data, message.from_user, message)

