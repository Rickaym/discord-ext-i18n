from typing import Any
from unittest.mock import Mock
from discord.ext.i18n.language import Language
from discord.abc import Messageable
from discord.ext.i18n.preprocess import (
    Detector,
    TranslationAgent,
    Translator,
)
from discord import (
    Guild,
    Interaction,
    InteractionResponse,
    Member,
    Message,
    TextChannel,
)
from tests.utils import MimeCache
from utils import generate_string_tuple, MimeTranslator, generate_long_num
from random import choice


TranslationAgent.cache = MimeCache()


def m_obj(base=object, **kwds):
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


def test_assembly():
    """
    Test whether if tokenizing and reassembling strings is
    correct.
    """
    test_strings = generate_string_tuple(30, 10, 50)
    mime = MimeTranslator()
    agent = TranslationAgent(Language.English, mime)
    for string in test_strings:
        assert string == agent.trans_assemble(string, agent.tokenize(string))


def test_translation_attempt():
    """
    Test whether if the translate method is properly put to use.
    """
    test_strings = generate_string_tuple(30, 10, 50)
    agent = TranslationAgent(Language.Swahili, MimeTranslator())
    for string in test_strings:
        assert agent.translate(string) == agent.trans_assemble(
            string, agent.tokenize(string)
        )


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
            "guild": m_obj(Guild, id=generate_long_num(12)),
        }
        kwds["channel"] = m_obj(
            TextChannel, id=generate_long_num(12), guild=kwds["guild"]
        )

        if base in (Message, InteractionResponse):
            kwds["author"] = m_obj(Member, id=generate_long_num(12))
            appr_keys.append("author")

        # Make sure that at least one of the available IDs reflect a
        # snowflake that has a preference
        item = pref_items[i]
        kwds[choice(appr_keys)].set_id(item[0])

        if base == InteractionResponse:
            kwds = {"_parent": m_obj(Interaction, message=m_obj(Message, **kwds))}

        test_objects[m_obj(base, id=i, **kwds)] = item

    agent = SubclassedDetector()
    for obj, item in test_objects.items():
        assert await agent.first_language_of(obj) is item[1]


def test_tokenize():
    def mk_token(start, name, end):
        return {
            "start_pos": start,
            "end_pos": end,
            "phrase": name,
        }

    agent = TranslationAgent(Language.English, Translator())
    test_map = {
        "What **is** your name?": [
            mk_token(0, "What ", 5),
            mk_token(7, "is", 9),
            mk_token(12, "your name?", 22),
        ],
    }
    agent.cache = Mock()
    for src, tokenls in test_map.items():
        assert agent.tokenize(src) == tokenls

