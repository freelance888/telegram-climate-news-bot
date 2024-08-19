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
