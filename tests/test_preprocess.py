import sys
from typing import Any


sys.path.append(r"D:\Programming\Python\Projects\disi18n")
from discord.ext.i18n.language import Language
from discord.abc import Messageable
from discord.ext.i18n.preprocess import (
    Detector,
    DetectionAgent,
    TranslationAgent,
    Translator,
)
from discord import Guild, Interaction, InteractionResponse, Member, Message, NotFound, TextChannel
from string import printable
from random import choice, randint, random


class MimeTranslator(Translator):
    def translate(self, payload: str, dest_lang: Language, src_lang: Language):
        return f"<As {dest_lang.name} from {src_lang} {payload}>"


def fobj(base=object, **kwds):
    """
    Creates an object with the desired base and worksaround the parent class's
    demands for a __slot__.
    """

    class Mime:
        __class__ = base

        def __init__(self):
            self.__dict__.update(kwds)

        def __repr__(self):
            return f"<{base.__name__} {', '.join(f'{k}={v}'for k, v in self.__dict__.items())}>"

        def __str__(self) -> str:
            return self.__repr__()

        def set_id(self, val):
            self.__dict__["id"] = val

        async def _get_channel(self):
            if self.__class__ != Messageable:
                raise NotImplementedError
            else:
                return self.channel

    return Mime()


def generate_string(min_slen: int, max_slen: int):
    return "".join(choice(printable) for i in range(randint(min_slen, max_slen)))


def generate_string_tuple(amount: int, min_slen: int, max_slen: int):
    test_strings = []
    for _ in range(amount):
        test_strings.append(generate_string(min_slen, max_slen))
    return tuple(test_strings)


def test_assembly():
    """
    Test whether if tokenizing and reassembling strings is
    correct.
    """
    test_strings = generate_string_tuple(10, 10, 50)
    agent = TranslationAgent(Language.English, MimeTranslator())
    for string in test_strings:
        payload, tks = agent.tokenize(string)
        assert string == agent.trans_assemble(payload, tks)


def test_translation_attempt():
    """
    Test whether if the translate method is properly put to use.
    """
    test_strings = generate_string_tuple(10, 10, 50)
    agent = TranslationAgent(Language.Swahili, MimeTranslator())
    for string in test_strings:
        assert agent.translate(string) == agent.trans_assemble(
            *agent.tokenize(string), dest_lang=Language.Swahili
        )


def generate_long_num(place: int):
    return int(random() * (10 ** place))


def generate_preferences(amount: int):
    preferences = {}
    langs = list(Language._member_map_.values())
    for _ in range(amount):
        preferences[generate_long_num(12)] = choice(langs)
    return preferences


async def test_detection():
    n_objs = 50
    prefs = generate_preferences(n_objs)
    pref_items = list(prefs.items())

    class SubclassedDetector(Detector):
        def __init__(self) -> None:
            self.preferences = prefs.copy()

        async def language_of(self, snowflake):
            return self.preferences.get(snowflake, None)

    test_objects = {}
    mock_classes = {0: Message, 1: InteractionResponse, 2: Messageable}

    for i in range(n_objs):
        base = mock_classes.get(i, choice(list(mock_classes.values())))
        appr_keys = ["channel", "guild"]
        kwds: Any = {
            "guild": fobj(Guild, id=generate_long_num(12)),
        }
        kwds["channel"] = fobj(TextChannel, id=generate_long_num(12), guild=kwds["guild"])

        if base in (Message, InteractionResponse):
            kwds["author"] = fobj(Member, id=generate_long_num(12))
            appr_keys.append("author")

        # Make sure that at least one of the available IDs reflect a
        # snowflake that has a preference
        item = pref_items[i]
        kwds[choice(appr_keys)].set_id(item[0])

        if base == InteractionResponse:
            kwds = {"_parent": fobj(Interaction, message=fobj(Message, **kwds))}

        test_objects[fobj(base, id=i, **kwds)] = item

    agent = SubclassedDetector()
    for obj, item in test_objects.items():
        assert await agent.first_language_of(obj) is item[1]


def test_lossless_encode():
    test_strings = generate_string_tuple(10, 10, 50)
    agent = DetectionAgent()
    langs = list(Language._member_map_.values())
    for string in test_strings:
        lang = choice(langs)
        enc_str = agent.encode_lang_str(string, lang)
        assert enc_str != string

        dec_str, dec_lang = agent.decode_lang_str(enc_str)
        assert lang is dec_lang
        assert dec_str == string
