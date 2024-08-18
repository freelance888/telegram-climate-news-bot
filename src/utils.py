from aiogram.dispatcher.handler import CancelHandler
from src.types import TELEGRAM_MESSAGE_MAX_LENGTH
from aiogram import types
import os

def _exit():
    raise CancelHandler()

def getDeepestValues(d):
    deepest_values = []
    for v in d.values():
        if isinstance(v, dict):
            deepest_values.extend(getDeepestValues(v))
        else:
            deepest_values.append(v)
    return deepest_values

def getMessageLink(chatId, messageId):
    chatId = str(chatId)

    if chatId.startswith('-100'):
        link = f"https://t.me/c/{chatId[4:]}/{messageId}"
    elif chatId.startswith('-'):
        link = f"https://t.me/c/{chatId[1:]}/{messageId}"
    else:
        link = f"https://t.me/c/{chatId}/{messageId}"

    return link

def strCut(s, limit):
    return s if len(s) <= limit else s[:limit - 3] + '...'

async def getTextFromDocumentOrMessage(message: types.Message):
    text = ""

    if message.content_type == types.ContentType.DOCUMENT:
        file = await message.document.download()
        text = open(file.name, 'r').read()
        os.remove(file.name)
        file.close()
    elif message.content_type == types.ContentType.TEXT:
        text = message.text

    return text

async def printAllMessage(message: types.Message, text: str):
    while len(text) > TELEGRAM_MESSAGE_MAX_LENGTH:
        await message.reply(text[:TELEGRAM_MESSAGE_MAX_LENGTH])
        text = text[TELEGRAM_MESSAGE_MAX_LENGTH:]

    await message.reply(text)

def getKeyByValue(dictionary: dict, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None
