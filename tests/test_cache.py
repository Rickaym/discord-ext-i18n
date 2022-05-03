from discord.ext.i18n.preprocess import TranslationAgent
from discord.ext.i18n.cache import Cache
from tests.utils import (
    generate_string_tuple,
    generate_rand_lang,
    MimeTranslator,
)


def test_caching():
    """
    Test whether if the translate tokens are cached properly.
    """
    test_strings = generate_string_tuple(30, 10, 50)
    translator = MimeTranslator()

    class SubMimeCache(Cache):
        def __init__(self) -> None:
            self.internal_cache = {}

        async def load_cache(self):
            pass

        async def save_cache(self):
            pass

        def task(self, c):
            pass

    for string in test_strings:
        lang = generate_rand_lang()
        agent = TranslationAgent(lang, translator)
        agent.cache = SubMimeCache()
        agent.translate(string)
        assert agent.cache.internal_cache == (
            {
                tk["phrase"]: {
                    lang.code: translator.translate(tk["phrase"], lang, lang)
                }
                for tk in agent.tokenize(string)
            }
        )
