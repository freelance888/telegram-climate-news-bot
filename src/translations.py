from src.types import TList, TKeys, ACTIVE_LANGS


TRANSLATIONS = {
    TList.RU: {
    }
}

def getLangCode(langCode: str):
    return langCode if langCode in ACTIVE_LANGS else TList.DEFAULT

def t(langCode: TList, key: str):
    langCode = getLangCode(langCode)

    if key not in TRANSLATIONS[langCode]:
        return TRANSLATIONS[TList.DEFAULT][key]

    return TRANSLATIONS[langCode][key]
