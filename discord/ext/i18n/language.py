from enum import Enum
from typing import Optional


LANG_CODE2EMOJIS = {
    "af": "🇿🇦",
    "sq": "🇦🇱",
    "am": "🇪🇹",
    "ar": "🇸🇦",
    "hy": "🇦🇲",
    "az": "🇦🇿",
    "eu": "🇪🇸",
    "be": "🇵🇱",
    "bn": "🇧🇩",
    "bs": "🇧🇦",
    "bg": "🇧🇬",
    "ca": "🇪🇸",
    "ceb": "🇵🇭",
    "ny": "🇲🇼",
    "zh-cn": "🇨🇳",
    "zh-tw": "🇨🇳",
    "co": "🇫🇷",
    "hr": "🇭🇷",
    "cs": "🇨🇿",
    "da": "🇩🇰",
    "nl": "🇳🇱",
    "en": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "eo": "🇬🇧",
    "et": "🇪🇪",
    "tl": "🇵🇭",
    "fi": "🇫🇮",
    "fr": "🇫🇷",
    "fy": "🇳🇱",
    "gl": "🇪🇸",
    "ka": "🇬🇪",
    "de": "🇩🇪",
    "el": "🇬🇷",
    "gu": "🇮🇳",
    "ht": "🇭🇹",
    "ha": "🇨🇫",
    "haw": "🇺🇸",
    "iw": "🇮🇱",
    "he": "🇮🇱",
    "hi": "🇮🇳",
    "hmn": "🇱🇦",
    "hu": "🇭🇺",
    "is": "🇮🇸",
    "ig": "🇳🇬",
    "id": "🇮🇩",
    "ga": "🇮🇪",
    "it": "🇮🇹",
    "ja": "🇯🇵",
    "jw": "🇮🇩",
    "kn": "🇮🇳",
    "kk": "🇰🇿",
    "km": "🇰🇭",
    "ko": "🇰🇷",
    "ku": "🇹🇷",
    "ky": "🇰🇬",
    "lo": "🇱🇦",
    "la": "🇵🇹",
    "lv": "🇱🇻",
    "lt": "🇱🇹",
    "lb": "🇩🇪",
    "mk": "🇲🇰",
    "mg": "🇲🇬",
    "ms": "🇲🇾",
    "ml": "🇮🇳",
    "mt": "🇲🇹",
    "mi": "🇳🇿",
    "mr": "🇮🇳",
    "mn": "🇲🇳",
    "my": "🇲🇲",
    "ne": "🇳🇵",
    "no": "🇳🇴",
    "or": "🇮🇳",
    "ps": "🇦🇫",
    "fa": "🇮🇷",
    "pl": "🇵🇱",
    "pt": "🇵🇹",
    "pa": "🇮🇳",
    "ro": "🇷🇴",
    "ru": "🇷🇺",
    "sm": "🇦🇸",
    "gd": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "sr": "🇷🇸",
    "st": "🇱🇸",
    "sn": "🇿🇼",
    "sd": "🇵🇰",
    "si": "🇱🇰",
    "sk": "🇸🇰",
    "sl": "🇦🇹",
    "so": "🇸🇴",
    "es": "🇪🇸",
    "su": "🇸🇩",
    "sw": "🇺🇬",
    "sv": "🇸🇪",
    "tg": "🇹🇯",
    "ta": "🇮🇳",
    "te": "🇮🇳",
    "th": "🇹🇭",
    "tr": "🇹🇷",
    "uk": "🇺🇦",
    "ug": "🇵🇰",
    "ug": "🇨🇳",
    "uz": "🇺🇿",
    "vi": "🇻🇳",
    "cy": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "xh": "🇿🇦",
    "yi": "🇮🇱",
    "yo": "🇳🇬",
    "zu": "🇿🇦",
}

LANG_CODE2NAME = {
    "af": "afrikaans",
    "sq": "albanian",
    "am": "amharic",
    "ar": "arabic",
    "hy": "armenian",
    "az": "azerbaijani",
    "eu": "basque",
    "be": "belarusian",
    "bn": "bengali",
    "bs": "bosnian",
    "bg": "bulgarian",
    "ca": "catalan",
    "ceb": "cebuano",
    "ny": "chichewa",
    "zh-cn": "chinese (simplified)",
    "zh-tw": "chinese (traditional)",
    "co": "corsican",
    "hr": "croatian",
    "cs": "czech",
    "da": "danish",
    "nl": "dutch",
    "en": "english",
    "eo": "esperanto",
    "et": "estonian",
    "tl": "filipino",
    "fi": "finnish",
    "fr": "french",
    "fy": "frisian",
    "gl": "galician",
    "ka": "georgian",
    "de": "german",
    "el": "greek",
    "gu": "gujarati",
    "ht": "haitian creole",
    "ha": "hausa",
    "haw": "hawaiian",
    "iw": "hebrew",
    "he": "hebrew",
    "hi": "hindi",
    "hmn": "hmong",
    "hu": "hungarian",
    "is": "icelandic",
    "ig": "igbo",
    "id": "indonesian",
    "ga": "irish",
    "it": "italian",
    "ja": "japanese",
    "jw": "javanese",
    "kn": "kannada",
    "kk": "kazakh",
    "km": "khmer",
    "ko": "korean",
    "ku": "kurdish (kurmanji)",
    "ky": "kyrgyz",
    "lo": "lao",
    "la": "latin",
    "lv": "latvian",
    "lt": "lithuanian",
    "lb": "luxembourgish",
    "mk": "macedonian",
    "mg": "malagasy",
    "ms": "malay",
    "ml": "malayalam",
    "mt": "maltese",
    "mi": "maori",
    "mr": "marathi",
    "mn": "mongolian",
    "my": "myanmar (burmese)",
    "ne": "nepali",
    "no": "norwegian",
    "or": "odia",
    "ps": "pashto",
    "fa": "persian",
    "pl": "polish",
    "pt": "portuguese",
    "pa": "punjabi",
    "ro": "romanian",
    "ru": "russian",
    "sm": "samoan",
    "gd": "scots gaelic",
    "sr": "serbian",
    "st": "sesotho",
    "sn": "shona",
    "sd": "sindhi",
    "si": "sinhala",
    "sk": "slovak",
    "sl": "slovenian",
    "so": "somali",
    "es": "spanish",
    "su": "sundanese",
    "sw": "swahili",
    "sv": "swedish",
    "tg": "tajik",
    "ta": "tamil",
    "te": "telugu",
    "th": "thai",
    "tr": "turkish",
    "uk": "ukrainian",
    "ur": "urdu",
    "ug": "uyghur",
    "uz": "uzbek",
    "vi": "vietnamese",
    "cy": "welsh",
    "xh": "xhosa",
    "yi": "yiddish",
    "yo": "yoruba",
    "zu": "zulu",
}

LANG_NAME2CODE = dict(map(reversed, LANG_CODE2NAME.items()))  # type: ignore


class Language(Enum):
    """
    An Enum for all the languages supported and has properties `emoji`,
    `name` and `code`.
    """

    Afrikaans = "af"
    Albanian = "sq"
    Amharic = "am"
    Arabic = "ar"
    Armenian = "hy"
    Azerbaijani = "az"
    Basque = "eu"
    Belarusian = "be"
    Bengali = "bn"
    Bosnian = "bs"
    Bulgarian = "bg"
    Catalan = "ca"
    Cebuano = "ceb"
    Chichewa = "ny"
    ChineseSimplified = "zh-cn"
    ChineseTraditional = "zh-tw"
    Corsican = "co"
    Croatian = "hr"
    Czech = "cs"
    Danish = "da"
    Dutch = "nl"
    English = "en"
    Esperanto = "eo"
    Estonian = "et"
    Filipino = "tl"
    Finnish = "fi"
    French = "fr"
    Frisian = "fy"
    Galician = "gl"
    Georgian = "ka"
    German = "de"
    Greek = "el"
    Gujarati = "gu"
    HaitianCreole = "ht"
    Hausa = "ha"
    Hawaiian = "haw"
    Hebrew = "he"
    Hindi = "hi"
    Hmong = "hmn"
    Hungarian = "hu"
    Icelandic = "is"
    Igbo = "ig"
    Indonesian = "id"
    Irish = "ga"
    Italian = "it"
    Japanese = "ja"
    Javanese = "jw"
    Kannada = "kn"
    Kazakh = "kk"
    Khmer = "km"
    Korean = "ko"
    KurdishKurmanji = "ku"
    Kyrgyz = "ky"
    Lao = "lo"
    Latin = "la"
    Latvian = "lv"
    Lithuanian = "lt"
    Luxembourgish = "lb"
    Macedonian = "mk"
    Malagasy = "mg"
    Malay = "ms"
    Malayalam = "ml"
    Maltese = "mt"
    Maori = "mi"
    Marathi = "mr"
    Mongolian = "mn"
    Myanmar = "my"
    Burmese = "my"
    Nepali = "ne"
    Norwegian = "no"
    Odia = "or"
    Pashto = "ps"
    Persian = "fa"
    Polish = "pl"
    Portuguese = "pt"
    Punjabi = "pa"
    Romanian = "ro"
    Russian = "ru"
    Samoan = "sm"
    ScotsGaelic = "gd"
    Serbian = "sr"
    Sesotho = "st"
    Shona = "sn"
    Sindhi = "sd"
    Sinhala = "si"
    Slovak = "sk"
    Slovenian = "sl"
    Somali = "so"
    Spanish = "es"
    Sundanese = "su"
    Swahili = "sw"
    Swedish = "sv"
    Tajik = "tg"
    Tamil = "ta"
    Telugu = "te"
    Thai = "th"
    Turkish = "tr"
    Ukrainian = "uk"
    Urdu = "ur"
    Uyghur = "ug"
    Uzbek = "uz"
    Vietnamese = "vi"
    Welsh = "cy"
    Xhosa = "xh"
    Yiddish = "yi"
    Yoruba = "yo"
    Zulu = "zu"

    @property
    def emoji(self) -> Optional[str]:
        return LANG_CODE2EMOJIS.get(self.value, None)

    @property
    def code(self) -> str:
        return self.value

    @property
    def name(self) -> str:
        return LANG_CODE2NAME[self.value]

    @staticmethod
    def from_code(lang_id: str) -> Optional["Language"]:
        return Language._value2member_map_.get(lang_id, None)  # type: ignore

    @staticmethod
    def from_name(name: str):
        return Language.from_code(LANG_NAME2CODE[name])
