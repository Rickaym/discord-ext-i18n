from unittest.mock import Mock
from discord.ext.i18n.language import Language
from discord.ext.i18n.preprocess import (
    TranslationAgent,
    Translator,
)
from utils import generate_string_tuple, MimeTranslator


# Test on string "```py\ndiscord-ext-i18n```"

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
        "\u200bAnd how does it \u200b**`affect you`**? <@368671236370464769> "
        "<:smile:123> \u200bif i may say so.":
            ["What does it", "mean", "to be?", "affect you"],
    }
    agent.cache = Mock()
    for src, tokenls in test_map.items():
        assert [a["phrase"] for a in agent.tokenize(src)] == tokenls
