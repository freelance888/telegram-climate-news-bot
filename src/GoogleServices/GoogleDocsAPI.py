from src.GoogleServices.GoogleService import GoogleService


class GoogleDocsAPI(GoogleService):
    def __init__(self):
        super().__init__('docs', 'v1', ['https://www.googleapis.com/auth/documents'])

    async def __insertText(self, requests: list, text: str, index: int):
        requests.append({
            'insertText': {
                'text': text,
                'location': {
                    'index': index
                }
            }
        })

    async def __updateLink(self, requests: list, startIndex: int, endIndex: int, url: str):
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': startIndex,
                    'endIndex': endIndex
                },
                'textStyle': {
                    'link': {
                        'url': url
                    }
                },
                'fields': 'link'
            }
        })

    async def getDocumentById(self, fileId: str):
        return await self.retry(self._service.documents().get(documentId=fileId))

    async def insertTable(self, documentId: str, table: list):
        if not table:
            raise Exception('Table is empty')

        tableColumnsLen = len(table[0])
        tableRowsLen = len(table)

        # create table
        requests = [
            {
                'insertTable': {
                    'rows': tableRowsLen,
                    'columns': tableColumnsLen,
                    'endOfSegmentLocation': {
                        'segmentId': '',
                    }
                }
            }
        ]

        await self.retry(self._service.documents().batchUpdate(documentId=documentId, body={'requests': requests}))
        document = await self.retry(self._service.documents().get(documentId=documentId))

        content = document.get('body').get('content')
        contentLen = len(content)
        docTable = content[contentLen - 2].get('table')

        if not docTable:
            raise Exception(f'Table not found - {documentId}')

        startIndex = docTable.get('tableRows')[tableRowsLen - 1].get('tableCells')[tableColumnsLen - 1].get('startIndex') + 1
        table = table[::-1]
        requests = []

        for row in table:
            row = row[::-1]
            for cell in row:
                if cell['type'] == 'text' and cell['src'] != '':
                    await self.__insertText(requests, cell['src'], startIndex)
                elif cell['type'] == 'link' and cell['src']:
                    cell['src'] = cell['src'][::-1]
                    linksLen = len(cell['src'])
                    i = 0
                    for link in cell['src']:
                        await self.__insertText(requests, link, startIndex)
                        await self.__updateLink(requests, startIndex, startIndex + len(link), link)
                        if i < linksLen - 1:
                            await self.__insertText(requests, '\n\n', startIndex)
                        i += 1
                startIndex -= 2

            startIndex -= 1

        await self.retry(self._service.documents().batchUpdate(documentId=documentId, body={'requests': requests}))

    async def getTableFromDocument(self, documentId: str):
        document = await self.getDocumentById(documentId)
        content = document.get('body').get('content')
        contentLen = len(content)
        docTable = content[contentLen - 2].get('table')

        if not docTable:
            raise Exception(f'Table not found - {documentId}')

        table = []

        for row in docTable.get('tableRows'):
            tableRow = []
            for cell in row.get('tableCells'):
                cell_text_parts: list[str] = []
                cell_link_urls: list[str] = []
                for block in cell.get('content', []):
                    para = block.get('paragraph')
                    if not para:
                        continue
                    for el in para.get('elements', []):
                        tr = el.get('textRun')
                        if not tr:
                            continue
                        content = tr.get('content') or ''
                        cell_text_parts.append(content)
                        url = (
                            tr.get('textStyle', {})
                            .get('link', {})
                            .get('url')
                        )
                        if url:
                            cell_link_urls.append(url)
                cell_text = ''.join(cell_text_parts)
                seen: set[str] = set()
                ordered_links: list[str] = []
                for u in cell_link_urls:
                    if u and u not in seen:
                        seen.add(u)
                        ordered_links.append(u)
                tableRow.append({
                    'type': 'text' if not ordered_links else 'link',
                    'src': ordered_links if ordered_links else cell_text
                })
            table.append(tableRow)

        return table