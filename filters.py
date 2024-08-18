from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config
from src.utils import getDeepestValues

class IsPersonalMsgFilter(BoundFilter):

    async def check(self, message: types.Message):
        return (message.chat.id == message.from_user.id)

class IsReplyFilter(BoundFilter):

        async def check(self, message: types.Message):
            return (message.reply_to_message)


class IsChatMsgFilter(BoundFilter):

    @staticmethod
    async def adminChat(message: types.Message):
        return (message.chat.id == config.ADMIN_CHAT)

    @staticmethod
    async def publicChat(message: types.Message):
        chatIds = getDeepestValues(config.CHANNEL_PUBLIC_CHATS)
        return (message.chat.id in chatIds)

    @staticmethod
    async def filter(message: types.Message):
        return await IsChatMsgFilter.adminChat(message) or await IsChatMsgFilter.publicChat(message)

    async def check(self, message: types.Message):
        return await self.filter(message)
