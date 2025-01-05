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

enEndText = """❗️If you want to learn more about the causes of increasing climate change, we recommend you to read the report:
<a href="https://be.creativesociety.com/storage/file-manager/climate-model-report-a4/ru/Climate%20Report.pdf">"On the progression of climatic disasters on Earth and their catastrophic consequences"</a>

It is very important to have an emergency backpack in case of unforeseen circumstances.
Share this information, because the more people realize the severity of climate change, the sooner the global scientific community will be able to come together to find solutions.
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
