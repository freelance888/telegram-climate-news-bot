import re
from aiogram.types import MessageEntity
from googletrans import Translator
import logging

translator = Translator()

async def __appedTotable(table: list, text: str, links: list = [], specialCaseFlag: bool = False):
    translatedText = ''
    bufText = text

    try:
        # some specific cases
        if specialCaseFlag:
            if 'https://rumble.com/c/CreativesocietyOfficial' in bufText:
                bufText = bufText.replace(
                    'https://rumble.com/c/CreativesocietyOfficial',
                    'https://rumble.com/c/CreativeSociety'
                )

        # do translation
        translated = translator.translate(bufText, src='ru', dest='en')
        translatedText = translated.text
    except Exception as e:
        logging.error(e)

    table.append([
        {'type': 'text', 'src': text},
        {'type': 'link', 'src': links},
        {'type': 'text', 'src': translatedText}
    ])

async def parseDigest(text: str, entities: list[MessageEntity]) -> list:
    urls = []
    keyWord = 'Источник'
    table = [[
        {'type': 'text', 'src': 'Ru'},
        {'type': 'text', 'src': 'Источники'},
        {'type': 'text', 'src': 'En'}
    ]]

    for entity in entities:
        if entity.type == 'text_link':
            urls.append(entity.url)

    text = text.split('\n\n')
    text = [t.strip() for t in text]

    tmpStr = ''
    for item in text:
        strings = item.split('\n')
        lastString = strings[-1].strip()

        if not lastString.startswith(keyWord):
            tmpStr += item + '\n\n'
            continue

        if tmpStr != '':
            await __appedTotable(table, tmpStr)
            tmpStr = ''

        keyWordsCount = len(re.split(f"{keyWord}\s+", item))
        links = []
        for i in range(keyWordsCount):
            links.append(urls.pop(0))

        await __appedTotable(table, item, links)

    if tmpStr != '':
        await __appedTotable(table, tmpStr, specialCaseFlag=True)

    return table
