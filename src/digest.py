import re
from aiogram.types import MessageEntity

# import logging
# from googletrans import Translator
# translator = Translator()
# try:
#     translated = translator.translate(text, src='ru', dest='en')
#     translatedText = translated.text
# except Exception as e:
#     logging.error(e)

enEndText = """❗️Learn about what is happening to our planet Earth and the true causes of climate change on the forum:

🔴 "Global Crisis. The Responsibility" 🔴

https://rumble.com/c/CreativeSociety

If you already understand the seriousness of what is happening, please share this information! Only by informing humanity and creating a public demand for the collaboration of scientists can we survive the escalating natural disasters!
"""

async def __appedTotable(table: list, text: str, links: list = [], translatedText: str = ''):
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
        translatedText = enEndText if 'https://rumble.com/c/CreativesocietyOfficial' in tmpStr else ''
        await __appedTotable(table, tmpStr, translatedText=translatedText)

    return table

async def buildDigest(table: list) -> str:
    table = table[1:]
    keyWord = 'Source'
    digest = f"<b><u>{table[0][2].get('src').strip()}</u></b>\n\n"
    table = table[1:]
    rowsLen = len(table)
    i = 1

    for row in table:
        links = row[1].get('src').split()
        enText = row[2].get('src')
        enText = enText.strip()
        enText = enText[:enText.find(keyWord)].strip()
        enText = enText.strip()

        if i != rowsLen:
            enText = re.sub(r'\n\n', '\n', enText)

        digest += f"{enText}\n"

        for link in links:
            digest += f'<a href="{link}">{keyWord}</a> '

        digest += '\n\n'
        i += 1

    return digest
