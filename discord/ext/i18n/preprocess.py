import inspect

from traceback import print_exception
from googletrans import Translator as GoogleTranslator
from typing import Any, Callable, Dict, List, Optional, Union
from discord.types.snowflake import Snowflake
from discord import Message, InteractionResponse, Webhook
from discord.abc import Messageable
from discord.ext.i18n.cache import Cache
from discord.ext.i18n.language import CODEBLOCK_LANGS, Language
from string import ascii_letters, punctuation, whitespace

punctuation += f"{whitespace}\u200b"
trailing_punctuation = punctuation.replace("?", "")


def isinstancemethod(func: Callable) -> bool:
    """
    Returns whether if a given function is a staticmethod or an
    instancemethod/classmethod.
    """
    return "self" in inspect.getfullargspec(func)[0]


class Detector:
    def __new__(cls, *_, **__):
        obj = super().__new__(cls)
        for item_name in dir(obj):
            item = getattr(obj, item_name, None)
            if callable(item):
                if hasattr(item, "__lang_getter__"):
                    Detector.language_of = item  # type: ignore
        return obj

    async def first_language_of(
        self, ctx: Union[Message, InteractionResponse, Messageable, Webhook]
    ):
        """
        Resolves the most precedent destination language from a context object.
        Other forms of checks are performed here.
        """
        guild_id = channel_id = author_id = dest_lang = None
        if isinstance(ctx, Message):
            author_id = ctx.author.id
            channel_id = ctx.channel.id
            if ctx.guild:
                guild_id = ctx.guild.id
        elif isinstance(ctx, Messageable):
            ch = await ctx._get_channel()
            channel_id = ch.id
            try:
                guild_id = ch.guild.id  # type: ignore
            except AttributeError:
                guild_id = None
        elif isinstance(ctx, Webhook):
            channel_id = ctx.channel_id
            guild_id = ctx.guild_id
        else:
            if ctx._parent.message and ctx._parent.message.guild:
                author_id = ctx._parent.message.author.id
                channel_id = ctx._parent.message.channel.id
                guild_id = ctx._parent.message.guild.id
            else:
                if ctx._parent.user:
                    author_id = ctx._parent.user.id
                channel_id = ctx._parent.channel_id
                guild_id = ctx._parent.guild_id

        if author_id:
            dest_lang = await self.language_of(author_id)
        if not dest_lang and channel_id:
            dest_lang = await self.language_of(channel_id)
        if not dest_lang and guild_id:
            dest_lang = await self.language_of(guild_id)
        return dest_lang

    @staticmethod
    async def language_of(snowflake: Snowflake) -> Optional[Language]:
        """
        Resolves a destination language for a snowflake.
        """
        return None

    @staticmethod
    def lang_getter(fn: Any):
        fn.__lang_getter__ = fn
        if not isinstancemethod(fn):
            Detector.language_of = staticmethod(fn)  # type: ignore
        return fn


class Translator:
    antecedent = GoogleTranslator()
    suppress_errors = True

    def __init__(self) -> None:
        """
        A simple wrapper around `googletrans.Translator` to allow the usage
        of Language enum elements as source and destination lang
        parameters.
        """

    def batch_translate(
        self, payloads: List[str], dest_lang: Language, src_lang: Language
    ):
        """
        Batch translates text from source language to destination language.
        """
        return [self.translate(text, dest_lang, src_lang) for text in payloads]

    def translate(self, payload: str, dest_lang: Language, src_lang: Language):
        """
        Translates text from source language to destination language.
        If the payload cannot be translate, the original string is returned.
        """
        try:
            return self.antecedent.translate(
                payload, dest=dest_lang.code, src=src_lang.code
            ).text
        except Exception as e:
            if not Translator.suppress_errors:
                print_exception(e.__class__, e, e.__traceback__)
            return payload

    @staticmethod
    def translator(fn: Any):
        pass


class TranslationAgent:
    decoratives = {
        "`": "`",
        "```": "```",
        "*": "*",
        "_": "_",
        "<@": ">",
        "<#": ">",
        "<@&": ">",
        "<!@": ">",
        "<:": ">",
        "(": ")",
        "\u200b": "\u200b",
    }
    # Add all possible entries codeblock starters
    decoratives.update({f"```{lang}\n": "```" for lang in CODEBLOCK_LANGS})

    ignored = {"<@", "<#", "<@&", "<!@", "<:", "\u200b"}
    cache = Cache()

    def __init__(
        self,
        src_lang: Language,
        dest_lang: Language,
        translator: Translator,
        enable_cache: bool = True,
    ) -> None:
        self.dest_lang = dest_lang
        self.src_lang = src_lang
        self.translator = translator
        if enable_cache:
            self.cache.load_cache_sync()
        self.enable_cache = enable_cache

    def translate(self, content: str):
        """
        Tokenizes the source string into segments to translate individually
        for better accuracy.
        """
        cached = self.trans_assemble(content, self.tokenize(content))
        return cached

    @staticmethod
    def similar_decors(char: str):
        return list(
            filter(
                lambda decor: decor.startswith(char),
                TranslationAgent.decoratives
                )
            )

    @staticmethod
    def tokenize(string: str):
        stoppage = {"\n"}

        stack, tokens = [], []
        i = 0

        def generate_token():
            """
            encouter: a decorative that invoked token generation
            """
            if not stack:
                return

            last_char = stack.pop(-1)
            start, end = last_char["pos"], i

            phrase = string[start:end]
            if not phrase.strip():
                return

            z_end = a_end = None
            # A token should not start or end with punctuations.
            for a, z in zip(phrase, phrase[::-1]):
                if z in trailing_punctuation and not z_end:
                    end -= 1
                else:
                    z_end = True

                if a in punctuation and not a_end:
                    start += 1
                else:
                    a_end = True
                if a_end and z_end:
                    break

            phrase = string[start:end]
            if phrase:
                tokens.append(
                    {"start_pos": start, "end_pos": end, "phrase": phrase}
                    )

        string_len = len(string)
        while i < string_len:
            char = string[i]

            if char not in ascii_letters:
                tmp_char = char
                tmp_pos = int(i)
                sample = TranslationAgent.similar_decors(char)
                while sample and i+1 != string_len:
                    i += 1
                    char += string[i]
                    sample = TranslationAgent.similar_decors(char)

                # loop oversteps one character if not EOF
                if i+1 != string_len:
                    char = char[:-1]
                    i -= 1

                if char not in TranslationAgent.decoratives:
                    char = tmp_char
                    i = tmp_pos

            char_pos = i
            if stack and stack[-1]["char"] in TranslationAgent.ignored:
                # Busy the loop as long as an ignored stack character
                # has not met it's end
                if char == TranslationAgent.decoratives[stack[-1]["char"]]:
                    stack.pop()
            elif char in stoppage:
                if stack and stack[-1]["char"] not in TranslationAgent.decoratives:
                    generate_token()
            elif (
                char in TranslationAgent.decoratives
                or char in TranslationAgent.decoratives.values()
            ):
                generate_token()
                # post is incremented by one since when making a token
                # we expect the starting position from one after the
                # decorative
                stack.append({"char": char, "pos": char_pos+1})
            elif not stack and char.strip():
                # stack is empty = start a new token
                stack.append({"char": char, "pos": char_pos})
            i += 1

        if stack:
            generate_token()

        return tokens

    def trans_assemble(self, payload: str, tokens: List[Dict[str, Any]]):
        """
        Re-assembles the tokens into a new string translated to the destination
        language.

        Parameters:
            payload: the original string that is tokenized
            tokens: a list of dictionaries about token data
        """
        new_str = list(payload)
        mitigate = 0

        for tk in tokens:
            phrase = tk["phrase"]

            if self.dest_lang:
                cached = None
                if self.enable_cache:
                    cached = self.cache.get_cache(phrase, self.dest_lang)

                if not cached:
                    cached = self.translator.translate(
                        phrase, dest_lang=self.dest_lang, src_lang=self.src_lang
                    )
                    if self.enable_cache:
                        self.cache.set_cache(phrase, self.dest_lang, cached)

                phrase = cached

            new_str[tk["start_pos"] + mitigate : tk["end_pos"] + mitigate] = phrase
            if tk["end_pos"] - tk["start_pos"] != len(phrase):
                mitigate += len(phrase) - (tk["end_pos"] - tk["start_pos"])
        return "".join(new_str)

    @staticmethod
    def clean_string(tokens: List[Dict[str, Any]]):
        return " ".join(tk["phrase"] for tk in tokens)
