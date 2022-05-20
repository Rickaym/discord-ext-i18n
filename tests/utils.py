from string import printable
from random import choice, randint, random
from typing import Any

from discord.ext.i18n.language import Language
from discord.ext.i18n.preprocess import Translator
from discord.ext.i18n.cache import Cache


def generate_string(min_slen: int, max_slen: int):
    return "".join(choice(printable) for i in range(randint(min_slen, max_slen)))


def generate_string_tuple(amount: int, min_slen: int, max_slen: int):
    test_strings = []
    for _ in range(amount):
        test_strings.append(generate_string(min_slen, max_slen))
    return tuple(test_strings)


def generate_rand_lang():
    return choice(list(Language.__members__.values()))


class MimeTranslator(Translator):
    def translate(self, payload: str, dest_lang, src_lang):
        return payload


class MimeCache(Cache):
    def __init__(self) -> None:
        self.cache_obj: Any = {}

    async def load_cache(self):
        pass

    async def save_cache(self):
        pass

    async def empty(self):
        pass

    def set_cache(self, src, lang, translated):
        if src in self.cache_obj:
            self.cache_obj[src][lang.code] = translated
        else:
            self.cache_obj[src] = {lang.code: translated}

    def get_cache(self, src, lang):
        return self.cache_obj.get(src, {}).get(lang.code, None)


def generate_long_num(place: int):
    return int(random() * (10 ** place))
