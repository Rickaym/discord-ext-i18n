from typing import Any, Dict, List, Coroutine, Callable, Optional, Union
from googletrans import Translator, LANGCODES
from discord.types.snowflake import Snowflake
from dataclasses import dataclass
from discord import Message, InteractionResponse
from discord.abc import Messageable


from i18n.language import Language
from i18n.cache import Cache

LanguageGetterFn = Callable[[None], Coroutine[Any, Any, None]]


@dataclass
class TokenList:
    payload: str
    tokens: List[Dict[str, Any]]

    def assemble(self, dest_lang=None):
        """
        Re-assembles the tokens into a new string with all fragments
        preserved.
        """
        new_str = list(self.payload)
        mitigate = 0
        for tk in self.tokens:
            proper = tk["phrase"]
            if dest_lang:
                proper = (
                    Translator()
                    .translate(
                        proper.strip().lower(), dest=dest_lang, src=LANGCODES["english"]
                    )
                    .text
                )
            new_str[tk["start_pos"] + mitigate : tk["end_pos"] + mitigate] = proper
            if tk["end_pos"] - tk["start_pos"] <= len(proper):
                mitigate += len(proper) - (tk["end_pos"] - tk["start_pos"])
        return "".join(new_str)

    def clean_string(self):
        return " ".join(tk["phrase"] for tk in self.tokens)


class DetectionAgent:
    delim = "\u200b"

    @staticmethod
    async def first_language_of(ctx: Union[Message, InteractionResponse, Messageable]):
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
                guild_id = ch.guild.id # type: ignore
            except AttributeError:
                guild_id = None
        elif ctx._parent.message and ctx._parent.message.guild:
            author_id = ctx._parent.message.id
            guild_id = ctx._parent.message.guild.id
            channel_id = ctx._parent.message.channel.id

        if author_id:
            dest_lang = await DetectionAgent.language_of(author_id)
        if not dest_lang and channel_id:
            dest_lang = await DetectionAgent.language_of(channel_id)
        if not dest_lang and guild_id:
            dest_lang = await DetectionAgent.language_of(guild_id)
        return dest_lang

    @staticmethod
    async def language_of(snowflake: Snowflake) -> Optional[Language]:
        """
        Retrieve the language of a snowflake, this is expected to be overridden
        in some manner.
        """
        return None

    @staticmethod
    def set_language_getter(getter: LanguageGetterFn):
        DetectionAgent.language_of = getter # type: ignore

    @staticmethod
    def encode_lang_str(s: str, lang: Language):
        """
        Append the language code into the string with a delimiter.
        """
        return f"{s}{DetectionAgent.delim}{lang.code}"

    @staticmethod
    def decode_lang_str(s: str):
        """
        Extract the language code from a string if it exists.
        """
        *content, lang_id = s.split(DetectionAgent.delim)
        if lang_id not in LANGCODES.keys():
            return s, None
        else:
            return content, lang_id

@dataclass
class TranslationAgent:
    lang: str

    def translate(self, content: str):
        tokens = self.tokenize(content)
        cached_trans = Cache.get_cache(self.lang, tokens.clean_string())
        if cached_trans:
            return cached_trans
        else:
            translated = tokens.assemble(dest_lang=self.lang)
            Cache.cache_trans(self.lang, tokens.clean_string(), translated)
            return translated

    @staticmethod
    def tokenize(payload: str):
        """
        Tokenizing the incoming payload allows us to temporarly fragment all meaningless or
        decorative characters to smoothen the translation process, afterwards all these
        fragments are appended back into precise locations.

        The general guideline to avoid loss of context from tokenizing is to avoid
        using markdown where it doesn't convey any meaning when separated.

        I.e. `What **is** your name?`
        """
        # An exhaustive list of all characters that marks the beginning
        # of a phrase that is decorated
        decoratives = ("`", "*", "_", "<", "\u200b")
        # An unexhaustive dict of all characters that marks the end
        # of a phrase that is decorated, when not specified, the delimiter is itself
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
                # If it is almost the end of the string and the characters are sensible
                # we'll add this and break out
                if i == len(payload) - 1 and not (char in decoratives or char == "\n"):
                    i += 1
                init, end = stack[-1]["pos"], i
                tokens.append(
                    {"start_pos": init, "end_pos": end, "phrase": payload[init:end]}
                )
                stack.pop(-1)

            if char in decoratives or char in con_decoratives.values():
                # Upon reaching a decorative, we'll start making a new token until
                # the same decorative is met
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
                            {"start_pos": init, "end_pos": end, "phrase": payload[init:end]}
                        )
                    stack.pop(-1)
                elif char not in con_decoratives.values() and (
                    not stack or stack[-1]["char"] not in ignorables
                ):
                    # The character shouldn't be a delimiter and the last frame of
                    # the stack must not be an ignorable - in a sense we won't insist
                    # on making new tokens inside an inconclusive ignorable
                    if char == "```":
                        while i < len(payload) and payload[i] != "\n":
                            i += 1
                        # Add 1 to starting pos to overcome newline char
                        i += 1
                    stack.append({"char": char, "pos": i})
            elif not stack and char.strip():
                # Phrase frames are appended when the stack is empty and the char
                # in stream is not a decorative, this is concluded in reach of any
                # decorative characters - phrase frames have numeric 0 as their char
                stack.append({"char": 0, "pos": i})
            i += 1
        return TokenList(payload, tokens)
