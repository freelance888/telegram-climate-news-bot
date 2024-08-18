from aiogram import types
from dispatcher import dp
from filters import IsChatMsgFilter
import config
from src.translations import t, getLangCode
from src.utils import _exit
from src.utils import getKeyByValue
from src.parse_digest import parseDigest
from src.init import googleDrive, googleDocs
import re
import config
from datetime import datetime


class ChatMessagingWithBotLogic:
    def __init__(self, message: types.Message):
        self.message = message
        self.langCode = getLangCode(message.from_user.language_code)
        self.chatLangCode = getKeyByValue(config.CHANNEL_PUBLIC_CHATS, self.message.chat.id)

    def _t(self, key):
        return t(self.langCode, key)

    async def _adminChatCommandsHandler(self):
        # commands here

        _exit()

    async def _publicChatTextHandler(self):
        text = self.message.text
        matchRes = re.match(r"^Дайджест\s+\d{2}\.\d{2}\.\d{2,4}(?:\s+\w+\s+(\d+))?", text)

        if matchRes:
            table = await parseDigest(text, self.message.entities)
            partNum = matchRes.group(1) if matchRes.group(1) else None
            date = datetime.now()
            curMonth = date.month if date.month > 9 else f"0{date.month}"
            curDay = date.day if date.day > 9 else f"0{date.day}"
            currentMonthName = date.strftime('%B')
            folderId = await googleDrive.createFolderIfNotExists(f"{date.year}", config.GS_ROOT_FOLDER_ID)
            folderId = await googleDrive.createFolderIfNotExists(f"{curMonth} ({currentMonthName})", folderId)
            fileId = await googleDrive.cloneFile(
                config.GS_TEMPLATE_FILE_ID,
                folderId,
                f"{date.year}-{curMonth}-{curDay} BN" + (f" part {partNum}" if partNum else "")
            )

            await googleDocs.insertTable(fileId, table)

        _exit()

    async def _textHandler(self):
        if await IsChatMsgFilter.adminChat(self.message):
            await self._adminChatCommandsHandler()
        elif await IsChatMsgFilter.publicChat(self.message):
            await self._publicChatTextHandler()

    async def run(self):
        contentType = self.message.content_type

        if contentType == types.ContentType.TEXT:
            await self._textHandler()


# Main handler
@dp.message_handler(IsChatMsgFilter(), content_types=types.ContentType.ANY)
async def main(message: types.Message):
    run = ChatMessagingWithBotLogic(message)
    await run.run()