import re
from html import escape
from typing import List, Optional

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

_SOURCE_URL_RE = re.compile(
    rf'Источник\s*\(?\s*(https?://[^\s\)\n<>]+)',
    re.IGNORECASE,
)


def _utf16_index_to_python_index(text: str, utf16_index: int) -> int:
    """Telegram entity offsets are UTF-16 code units; map to Python string index."""
    u = 0
    for i, ch in enumerate(text):
        if u >= utf16_index:
            return i
        u += 2 if ord(ch) > 0xFFFF else 1
    return len(text)


def _extract_source_links_from_text(item: str) -> list[str]:
    """
    URLs that belong to this news block only: each must follow the word «Источник».
    Stray links in the body (e.g. after 🟣 without «Источник») are ignored.
    """
    raw = _SOURCE_URL_RE.findall(item)
    cleaned: list[str] = []
    for u in raw:
        u = u.rstrip(').,;')
        if u and u not in cleaned:
            cleaned.append(u)
    return cleaned


def _message_entity_type_name(entity: MessageEntity) -> str:
    t = entity.type
    if isinstance(t, str):
        return t
    v = getattr(t, 'value', None)
    if isinstance(v, str):
        return v
    return str(t).lower().split('.')[-1]


def _urls_from_entities_for_item(
    full_text: str,
    entities: Optional[List[MessageEntity]],
    item: str,
) -> list[str]:
    """
    URLs from Telegram text_link / url entities on the last line only (where sources are).

    Needed when the line looks like «ИсточникИсточникИсточник» with no spaces: each word is a
    separate hyperlink and there is no «https://…» in the plain text, so regex cannot see them.
    """
    if not entities or not full_text:
        return []
    item_start = full_text.find(item)
    if item_start < 0:
        return []
    item_end = item_start + len(item)
    last_nl = item.rfind('\n')
    tail = item[last_nl + 1:] if last_nl >= 0 else item
    tail_stripped = tail.strip()
    if not tail_stripped.lower().startswith('источник'):
        return []
    tail_start = item_start + (len(item) - len(tail))
    out: list[str] = []
    for entity in sorted(entities, key=lambda e: e.offset):
        et = _message_entity_type_name(entity)
        if et not in ('text_link', 'url'):
            continue
        e_start = _utf16_index_to_python_index(full_text, entity.offset)
        e_end = _utf16_index_to_python_index(full_text, entity.offset + entity.length)
        if e_start < tail_start or e_end > item_end:
            continue
        if et == 'text_link' and getattr(entity, 'url', None):
            out.append(entity.url)
        elif et == 'url':
            out.append(full_text[e_start:e_end])
    deduped: list[str] = []
    for u in out:
        u = (u or '').strip()
        if u and u not in deduped:
            deduped.append(u)
    return deduped


def _coalesce_source_links(
    item: str,
    full_text: str,
    entities: Optional[List[MessageEntity]],
) -> list[str]:
    """
    Prefer entity-based URLs when there are at least as many as in the plain text: covers
    «ИсточникИсточник…» without spaces. Otherwise use regex matches (visible https://…).
    """
    from_text = _extract_source_links_from_text(item)
    from_ent = _urls_from_entities_for_item(full_text, entities, item)
    if from_ent and len(from_ent) >= len(from_text):
        return from_ent
    if from_text:
        return from_text
    return from_ent


async def __appedTotable(table: list, text: str, links: list = [], translatedText: str = ''):
    table.append([
        {'type': 'text', 'src': text},
        {'type': 'link', 'src': links},
        {'type': 'text', 'src': translatedText}
    ])

async def parseDigest(text: str, entities: list[MessageEntity]) -> list:
    keyWord = 'Источник'
    table = [[
        {'type': 'text', 'src': 'Ru'},
        {'type': 'text', 'src': 'Источники'},
        {'type': 'text', 'src': 'En'}
    ]]

    full_text = text
    text = text.split('\n\n')
    text = [t.strip() for t in text]

    tmpStr = ''
    for item in text:
        strings = item.split('\n')
        lastString = strings[-1].strip()

        if not lastString.lower().startswith(keyWord.lower()):
            tmpStr += item + '\n\n'
            continue

        if tmpStr != '':
            await __appedTotable(table, tmpStr)
            tmpStr = ''

        links = _coalesce_source_links(item, full_text, entities)

        await __appedTotable(table, item, links)

    if tmpStr != '':
        translatedText = enEndText if 'https://rumble.com/c/CreativesocietyOfficial' in tmpStr else ''
        await __appedTotable(table, tmpStr, translatedText=translatedText)

    return table


def _normalize_links_cell(links_cell) -> list[str]:
    if isinstance(links_cell, list):
        parts = links_cell
    else:
        parts = str(links_cell or '').split()
    out: list[str] = []
    for p in parts:
        p = (p or '').strip()
        if p and p not in out:
            out.append(p)
    return out


async def buildDigest(table: list) -> str:
    if len(table) < 2:
        return ''

    data = table[1:]
    keyWord = 'Source'
    digest = ''

    # Optional first row: title only in En column (Ru + sources empty)
    if data:
        ru0 = (data[0][0].get('src') or '').strip()
        en0 = (data[0][2].get('src') or '').strip()
        links0 = _normalize_links_cell(data[0][1].get('src'))
        if not ru0 and not links0 and en0:
            digest = f"<b><u>{escape(en0)}</u></b>\n\n"
            data = data[1:]

    rows_len = len(data)
    for i, row in enumerate(data, start=1):
        if len(row) < 3:
            continue

        links = _normalize_links_cell(row[1].get('src'))
        en_text = (row[2].get('src') or '').strip()
        if keyWord in en_text:
            en_text = en_text[:en_text.find(keyWord)].strip()

        if i != rows_len:
            en_text = re.sub(r'\n\n', '\n', en_text)

        digest += f"{en_text}\n"

        for link in links:
            link = (link or '').strip()
            if not link:
                continue
            safe_href = escape(link, quote=True)
            digest += f'<a href="{safe_href}">{keyWord}</a> '

        digest += '\n\n'

    return digest
