import re
from aiogram.types import MessageEntity

async def parseDigest(text: str, entities: list[MessageEntity]) -> list:
    urls = []
    keyWord = 'Источник'
    table = [
        ['Ru', 'Источники', 'En']
    ]

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
            table.append([tmpStr, '', ''])
            tmpStr = ''

        keyWordsCount = len(re.split(f"{keyWord}\s+", item))
        links = ''
        for i in range(keyWordsCount):
            links += urls.pop(0) + "\n\n"
        links = links.strip()

        table.append([item, links, ''])

    if tmpStr != '':
        table.append([tmpStr, '', ''])

    return table
