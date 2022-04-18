from googletrans import LANGCODES
from googletrans import LANGUAGES as LANGUAGE_MAP
from enum import Enum

LANGMOJIS = {
    "afrikaans": "🇿🇦",
    "albanian": "🇦🇱",
    "amharic": "🇪🇹",
    "arabic": "🇸🇦",
    "armenian": "🇦🇲",
    "azerbaijani": "🇦🇿",
    "basque": "🇪🇸",
    "belarusian": "🇵🇱",
    "bengali": "🇧🇩",
    "bosnian": "🇧🇦",
    "bulgarian": "🇧🇬",
    "catalan": "🇪🇸",
    "cebuano": "🇵🇭",
    "chichewa": "🇲🇼",
    "chinese (simplified)": "🇨🇳",
    "chinese (traditional)": "🇨🇳",
    "corsican": "🇫🇷",
    "croatian": "🇭🇷",
    "czech": "🇨🇿",
    "danish": "🇩🇰",
    "dutch": "🇳🇱",
    "english": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "esperanto": "🇬🇧",
    "estonian": "🇪🇪",
    "filipino": "🇵🇭",
    "finnish": "🇫🇮",
    "french": "🇫🇷",
    "frisian": "🇳🇱",
    "galician": "🇪🇸",
    "georgian": "🇬🇪",
    "german": "🇩🇪",
    "greek": "🇬🇷",
    "gujarati": "🇮🇳",
    "haitian creole": "🇭🇹",
    "hausa": "🇨🇫",
    "hawaiian": "🇺🇸",
    "hebrew": "🇮🇱",
    "hindi": "🇮🇳",
    "hmong": "🇱🇦",
    "hungarian": "🇭🇺",
    "icelandic": "🇮🇸",
    "igbo": "🇳🇬",
    "indonesian": "🇮🇩",
    "irish": "🇮🇪",
    "italian": "🇮🇹",
    "japanese": "🇯🇵",
    "javanese": "🇮🇩",
    "kannada": "🇮🇳",
    "kazakh": "🇰🇿",
    "khmer": "🇰🇭",
    "korean": "🇰🇷",
    "kurdish (kurmanji)": "🇹🇷",
    "kyrgyz": "🇰🇬",
    "lao": "🇱🇦",
    "latin": "🇵🇹",
    "latvian": "🇱🇻",
    "lithuanian": "🇱🇹",
    "luxembourgish": "🇩🇪",
    "macedonian": "🇲🇰",
    "malagasy": "🇲🇬",
    "malay": "🇲🇾",
    "malayalam": "🇮🇳",
    "maltese": "🇲🇹",
    "maori": "🇳🇿",
    "marathi": "🇮🇳",
    "mongolian": "🇲🇳",
    "myanmar (burmese)": "🇲🇲",
    "nepali": "🇳🇵",
    "norwegian": "🇳🇴",
    "odia": "🇮🇳",
    "pashto": "🇦🇫",
    "persian": "🇮🇷",
    "polish": "🇵🇱",
    "portuguese": "🇵🇹",
    "punjabi": "🇮🇳",
    "romanian": "🇷🇴",
    "russian": "🇷🇺",
    "samoan": "🇦🇸",
    "scots gaelic": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "serbian": "🇷🇸",
    "sesotho": "🇱🇸",
    "shona": "🇿🇼",
    "sindhi": "🇵🇰",
    "sinhala": "🇱🇰",
    "slovak": "🇸🇰",
    "slovenian": "🇦🇹",
    "somali": "🇸🇴",
    "spanish": "🇪🇸",
    "sundanese": "🇸🇩",
    "swahili": "🇺🇬",
    "swedish": "🇸🇪",
    "tajik": "🇹🇯",
    "tamil": "🇮🇳",
    "telugu": "🇮🇳",
    "thai": "🇹🇭",
    "turkish": "🇹🇷",
    "ukrainian": "🇺🇦",
    "urdu": "🇵🇰",
    "uyghur": "🇨🇳",
    "uzbek": "🇺🇿",
    "vietnamese": "🇻🇳",
    "welsh": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "xhosa": "🇿🇦",
    "yiddish": "🇮🇱",
    "yoruba": "🇳🇬",
    "zulu": "🇿🇦",
}

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
    def emoji(self):
        return LANGMOJIS[LANGCODES[self.value]]

    @property
    def code(self):
        return self.value

    @property
    def name(self):
        return LANGUAGE_MAP[self.value].title()
