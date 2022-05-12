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
from utils import generate_string_tuple, MimeTranslator, generate_long_num
from random import choice


# Test on string "```py\ndiscord-ext-i18n```"


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


def test_token_assembly():
    """
    Test whether if tokenizing and reassembling strings is
    correct.
    """
    test_strings = generate_string_tuple(30, 10, 50)
    mime = MimeTranslator()
    agent = TranslationAgent(Language.English, Language.English, mime, False)
    for string in test_strings:
        assert string == agent.trans_assemble(string, agent.tokenize(string))


def test_translation_attempt():
    """
    Test whether if the translate method is properly put to use.
    """
    test_strings = generate_string_tuple(30, 10, 50)
    agent = TranslationAgent(Language.English, Language.Swahili, MimeTranslator(), False)
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


def test_tokenize_phrases():
    agent = TranslationAgent(
        Language.English, Language.English, Translator(), False
        )
    test_map = {
        "What **is** your name?":
            ["What", "is", "your name?"],
        "```py\nHow do you mean?\n```":
            ["How do you mean?"],
        "I shall never! **let them buy their wedding**.":
            ["I shall never", "let them buy their wedding"],
        "Can <@368671236370464769> make sure that one eats puddin?":
            ["Can", "make sure that one eats puddin?"],
        "<@368671236370464769> needs to hold the spread of **lies**":
            ["needs to hold the spread of", "lies"],
        "Insiders <@368671236370464769> fighting for insiders. "
        "```diff\n- TIME TO STOP\n```":
            ["Insiders", "fighting for insiders", "TIME TO STOP"],
        "```js\n- What does it mean to be?```\n"
        "And how does it affect you? <@368671236370464769> <:smile:123>":
            ["What does it mean to be?", "And how does it affect you?"],
        "Insiders <@368671236370464769> fighting for insiders. "
        "\u200b```diff\n- TIME TO STOP\n```":
            ["Insiders", "fighting for insiders"],
        "```js\n- What does it **mean** to be?```\n"
        "\u200bAnd how does it \u200baffect you? <@368671236370464769> "
        "<:smile:123> \u200bif i may say so.":
            ["What does it", "mean", "to be?", "affect you?"],
    }
    agent.cache = Mock()
    for src, tokenls in test_map.items():
        assert [a["phrase"] for a in agent.tokenize(src)] == tokenls
