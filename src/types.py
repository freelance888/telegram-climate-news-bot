class TList():
    DEFAULT = 'en'

    RU = 'ru'
    EN = 'en'
    ES = 'es'
    AR = 'ar'
    FR = 'fr'
    DE = 'de'
    IT = 'it'
    JA = 'ja'
    ZH = 'zh'
    KO = 'ko'
    PT = 'pt'
    PL = 'pl'
    UK = 'uk'
    UZ = 'uz'

ACTIVE_LANGS = {
    TList.EN: {'flag': '🇬🇧', 'name': 'English'},
    TList.ES: {'flag': '🇪🇸', 'name': 'Español'},
    TList.DE: {'flag': '🇩🇪', 'name': 'Deutsch'},
    TList.FR: {'flag': '🇫🇷', 'name': 'Français'},
    TList.IT: {'flag': '🇮🇹', 'name': 'Italiano'},
    TList.PT: {'flag': '🇵🇹', 'name': 'Português'},
    TList.PL: {'flag': '🇵🇱', 'name': 'Polski'},
    TList.UK: {'flag': '🇺🇦', 'name': 'Українська'},
    TList.RU: {'flag': '🇷🇺', 'name': 'Русский'},
    TList.UZ: {'flag': '🇺🇿', 'name': 'Oʻzbekcha'},
    TList.AR: {'flag': '🇸🇦', 'name': 'العربية'},
    TList.ZH: {'flag': '🇨🇳', 'name': '中文'},
    TList.JA: {'flag': '🇯🇵', 'name': '日本語'},
}

class TKeys():
    @staticmethod
    def getKeyWithPostfix(key: str, postfix: int):
        return getattr(TKeys, f'{key}_{postfix}')

    # Commands


class Commands():
    START = 'start'

class ChatType():
    ADMINS = 'admins'

TELEGRAM_MESSAGE_MAX_LENGTH = 4096
