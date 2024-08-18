from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import asyncio
import config

class GoogleService:
    MAX_RETRIES = 5

    def __getCredentials(self, scopes: list):
        return service_account.Credentials.from_service_account_file(config.GS_SERVICE_ACCOUNT_FILE, scopes=scopes)

    def __init__(self, serviceName: str, version: str, scopes: list) -> None:
        self._service = build(serviceName, version, credentials=self.__getCredentials(scopes))

    async def retry(self, build):
        for i in range(self.MAX_RETRIES):
            try:
                return build.execute()
            except HttpError as error:
                if error.resp.status in [500, 502, 503, 504]:
                    await asyncio.sleep(2 ** i)
                else:
                    raise
            except BrokenPipeError:
                await asyncio.sleep(2 ** i)

        raise Exception('Max retries exceeded')
