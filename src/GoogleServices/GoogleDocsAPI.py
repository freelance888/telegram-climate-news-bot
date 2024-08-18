from src.GoogleServices.GoogleService import GoogleService


class GoogleDocsAPI(GoogleService):
    def __init__(self):
        super().__init__('docs', 'v1', ['https://www.googleapis.com/auth/documents'])

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
                if cell != '':
                    requests.append({
                        'insertText': {
                            'text': cell,
                            'location': {
                                'index': startIndex
                            }
                        }
                    })
                startIndex -= 2

            startIndex -= 1

        await self.retry(self._service.documents().batchUpdate(documentId=documentId, body={'requests': requests}))
