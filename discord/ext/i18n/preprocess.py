from cgi import print_exception
import inspect

from googletrans import Translator as GoogleTranslator
from typing import Any, Callable, Dict, List, Optional, Union
from discord.types.snowflake import Snowflake
from discord import Message, InteractionResponse
from discord.abc import Messageable
from discord.ext.i18n.cache import Cache
from discord.ext.i18n.language import LANG_CODE2NAME, Language
from string import punctuation, whitespace

punctuation += whitespace


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
        self, ctx: Union[Message, InteractionResponse, Messageable]
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


class DetectionAgent:
    delim = "\u200b"

    @staticmethod
    def encode_lang_str(s: str, lang: Language):
        """
        Append the language code into the string with a delimiter.
        """
        if not s:
            return f"{DetectionAgent.delim}{lang.code}"

        detection = Translator.antecedent.detect(s)
        if lang.code != detection.lang:
            return f"{s}{DetectionAgent.delim}{lang.code}"
        else:
            return s

    @staticmethod
    def decode_lang_str(s: str):
        """
        Extract the language code from a string if it exists.
        """
        *content, lang_id = s.split(DetectionAgent.delim)
        if lang_id not in LANG_CODE2NAME.keys():
            return s, None
        else:
            return DetectionAgent.delim.join(content) or None, Language.from_code(
                lang_id
            )


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
        self,
        payloads: List[str],
        dest_lang: Language,
        src_lang: Language
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
    cache = Cache()
    decoratives = {"`": "`", "*": "*", "_": "_", "<": ">", "(": ")", "\u200b": "\u200b"}

    def __init__(
        self, dest_lang: Language, translator: Translator, enable_cache: bool = True
    ) -> None:
        self.dest_lang = dest_lang
        self.translator = translator
        self.enable_cache = enable_cache

    def translate(self, content: str):
        """
        Tokenizes the source string into segments to translate individually
        for better accuracy.
        """
        cached = self.trans_assemble(content, self.tokenize(content))
        return cached

    @staticmethod
    def tokenize(string: str):
        stoppage = {"\n"}
        ignored = {">": "<", "\u200b": "\u200b"}
        stack, tokens = [], []

        i = 0

        def generate_token(encounter: str = ""):
            """
            encouter: a decorative that invoked token generation
            """
            if encounter in ignored and stack[-1]["char"] == ignored[encounter]:
                return
            last_char = stack.pop(-1)
            start, end = last_char["pos"], i

            phrase = string[start:end]
            if not phrase.strip():
                return

            z_end = a_end = None
            # A token should not start or end with punctuations.
            for a, z in zip(phrase, phrase[::-1]):
                if z in punctuation and not z_end:
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
            tokens.append({"start_pos": start, "end_pos": end, "phrase": phrase})

        while i < len(string):
            char = string[i]
            if char in stoppage:
                if stack:
                    generate_token()
            elif (
                char in TranslationAgent.decoratives
                or char in TranslationAgent.decoratives.values()
            ):
                if stack:
                    generate_token(char)
                stack.append({"char": char, "pos": i + 1})
            elif not stack and char.strip():
                # stack is empty = start a new token
                stack.append({"char": char, "pos": i})
            i += 1
        else:
            # token starter left in stack
            if stack and stack[-1]["char"] not in ignored:
                generate_token()

        return tokens

    @staticmethod
    def tokenize_legacy(payload: str):
        """
        Tokenizing the incoming payload allows us to temporarly fragment all
        meaningless or decorative characters to smoothen the translation
        process, afterwards all these fragments are appended back into precise
        with the most optimal amount of context reserved.

        The general guideline to avoid loss of context from tokenizing is to
        avoid using markdown where it doesn't convey any meaning when
        separated.

        I.e. `What **is** your name?`
        """
        # An exhaustive list of all characters that marks the beginning
        # of a phrase that is decorated
        decoratives = ("`", "*", "_", "<", "\u200b")

        # An unexhaustive dict of all characters that marks the end
        # of a phrase that is decorated, when not specified, the delimiter is
        # itself
        con_decoratives = {"<": ">"}

        # A list of decoratives where the inner text is ignored
        ignorables = ("<", "\u200b")

        stack, tokens = [], []
        i = 0
        while i < len(payload):
            char = payload[i]
            if (
                stack
                and stack[-1]["char"] == 0
                and (char == "\n" or char in decoratives or i == len(payload) - 1)
            ):
                # At the end of the string and if the characters are sensible
                # we'll add this and break out
                if i == len(payload) - 1 and not (char in decoratives or char == "\n"):
                    i += 1
                init, end = stack[-1]["pos"], i
                tokens.append(
                    {"start_pos": init, "end_pos": end, "phrase": payload[init:end]}
                )
                stack.pop(-1)

            if char in decoratives or char in con_decoratives.values():
                # Upon reaching a decorative, we'll start making a new token
                # until the same decorative is met
                i += 1
                while i < len(payload) and payload[i] in char:
                    char += payload[i]
                    i += 1

                if stack and char == con_decoratives.get(
                    stack[-1]["char"], stack[-1]["char"]
                ):
                    init, end = stack[-1]["pos"], i - len(char)
                    if stack[-1]["char"] not in ignorables:
                        tokens.append(
                            {
                                "start_pos": init,
                                "end_pos": end,
                                "phrase": payload[init:end],
                            }
                        )
                    stack.pop(-1)
                elif char not in con_decoratives.values() and (
                    not stack or stack[-1]["char"] not in ignorables
                ):
                    # The character shouldn't be a delimiter and the last frame
                    # of the stack must not be an ignorable - in a sense we
                    # won't insist on making new tokens inside an inconclusive
                    # ignorable
                    if char == "```":
                        while i < len(payload) and payload[i] != "\n":
                            i += 1
                        # Add 1 to starting pos to overcome newline char
                        i += 1
                    stack.append({"char": char, "pos": i})
            elif not stack and char.strip():
                # Phrase frames are appended when the stack is empty and the
                # char in stream is not a decorative, this is concluded in
                # reach of any decorative characters - phrase frames have
                # numeric 0 as their char
                stack.append({"char": 0, "pos": i})
            i += 1
        for tk in tokens:
            if tk["phrase"].endswith(" "):
                tk["phrase"] = tk["phrase"][:-1]
                tk["end_pos"] -= 1
        return tokens

    def trans_assemble(
        self,
        payload: str,
        tokens: List[Dict[str, Any]],
        src_lang: Language = Language.English,
    ):
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
                        phrase, dest_lang=self.dest_lang, src_lang=src_lang
                    )
                    if self.enable_cache:
                        self.cache.set_cache(phrase, self.dest_lang, cached)

                phrase = cached

            new_str[tk["start_pos"] + mitigate: tk["end_pos"] + mitigate] = phrase
            if tk["end_pos"] - tk["start_pos"] != len(phrase):
                mitigate += len(phrase) - (tk["end_pos"] - tk["start_pos"])
        return "".join(new_str)

    @staticmethod
    def clean_string(tokens: List[Dict[str, Any]]):
        return " ".join(tk["phrase"] for tk in tokens)
