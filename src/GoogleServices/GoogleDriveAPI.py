from src.GoogleServices.GoogleService import GoogleService


class GoogleDriveAPI(GoogleService):
    def __init__(self):
        super().__init__('drive', 'v3', ['https://www.googleapis.com/auth/drive'])

    async def cloneFile(self, fileId: str, folderId: str, name: str):
        copy_metadata = {
            'name': name,
            'parents': [folderId]
        }

        res = self._service.files().copy(fileId=fileId, body=copy_metadata, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()

        return res.get('id')

    async def createFolderIfNotExists(self, name: str, parentFolderId: str):
        response = self._service.files().list(
            q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{parentFolderId}' in parents",
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        folder = next((file for file in response.get('files', [])), None)

        if folder:
            return folder['id']

        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parentFolderId]
        }

        created_folder = self._service.files().create(
            body=folder_metadata, fields='id'
        ).execute()

        return created_folder['id']
