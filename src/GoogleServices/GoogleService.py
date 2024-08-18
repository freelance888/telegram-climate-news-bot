from google.oauth2 import service_account
from googleapiclient.discovery import build
import config

class GoogleService:
    def __getCredentials(self, scopes: list):
        return service_account.Credentials.from_service_account_file(config.GS_SERVICE_ACCOUNT_FILE, scopes=scopes)

    def __init__(self, serviceName: str, version: str, scopes: list) -> None:
        self._service = build(serviceName, version, credentials=self.__getCredentials(scopes))
