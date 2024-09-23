from aiogram import types
from dispatcher import dp
from filters import IsChatMsgFilter
from src.translations import t, getLangCode
from src.utils import _exit
from src.utils import getKeyByValue
from src.init import googleDrive, googleDocs
from config import CHANNEL_PUBLIC_CHATS, GS_ROOT_FOLDER_ID, GS_TEMPLATE_FILE_ID, ADMIN_CHAT, NEW_DIGEST_CREATED_NOTIFICATION_USERS
from src.digest import parseDigest, buildDigest
from datetime import datetime
import logging
import re


class ChatMessagingWithBotLogic:
    def __init__(self, message: types.Message):
        self.message = message
        self.langCode = getLangCode(message.from_user.language_code)
        self.chatLangCode = getKeyByValue(CHANNEL_PUBLIC_CHATS, self.message.chat.id)

    def _t(self, key):
        return t(self.langCode, key)

    async def _adminChatCommandsHandler(self):
        text = self.message.text
        matchRes = re.match(r"^\/digest\s+(.+)$", text)

        if matchRes:
            try:
                waitMsg = await self.message.reply('⏳')
                fileId = matchRes.group(1)
                fileId = fileId.split('/')[-2] if fileId.startswith('https://docs.google.com/document/d/') else fileId
                table = await googleDocs.getTableFromDocument(fileId)
                digest = await buildDigest(table)
                await self.message.reply(digest)
            except Exception as e:
                logging.error(f"Error: {e}")
                await self.message.reply("⚠️ Error occurred while building digest. Please try again or contact the developer.")
            finally:
                await waitMsg.delete()

        _exit()

    async def _publicChatTextHandler(self):
        text = self.message.text
        matchRes = re.match(r"^Дайджест\s+\d{2}\.\d{2}\.\d{2,4}(?:\s+\w+\s+(\d+))?", text)

        if matchRes:
            date = datetime.now()

            logging.info(f"[{date}] Digest ({matchRes.group(0)}) was requested")

            table = await parseDigest(text, self.message.entities)
            partNum = matchRes.group(1) if matchRes.group(1) else None
            curMonth = date.month if date.month > 9 else f"0{date.month}"
            curDay = date.day if date.day > 9 else f"0{date.day}"
            currentMonthName = date.strftime('%B')
            folderId = await googleDrive.createFolderIfNotExists(f"{date.year}", GS_ROOT_FOLDER_ID)
            folderId = await googleDrive.createFolderIfNotExists(f"{curMonth} ({currentMonthName})", folderId)
            fileId = await googleDrive.cloneFile(
                GS_TEMPLATE_FILE_ID,
                folderId,
                f"{date.year}-{curMonth}-{curDay} BN" + (f" part {partNum}" if partNum else "")
            )

            await googleDocs.insertTable(fileId, table)
            logging.info(f"[{datetime.now()}] Digest was created: {fileId}")

            notificationMessage = f"🔔 New digest was created:\nhttps://docs.google.com/document/d/{fileId}\n\n{NEW_DIGEST_CREATED_NOTIFICATION_USERS}"
            await self.message.bot.send_message(ADMIN_CHAT, notificationMessage)


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