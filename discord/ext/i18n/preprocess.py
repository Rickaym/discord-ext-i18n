from googletrans import Translator as GoogleTranslator
from typing import Any, Dict, List, Optional, Union
from discord.types.snowflake import Snowflake
from discord import Message, InteractionResponse
from discord.abc import Messageable
from discord.ext.i18n.language import LANG_CODE2NAME, Language


class Detector:
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
        elif ctx._parent.message and ctx._parent.message.guild:
            author_id = ctx._parent.message.author.id
            guild_id = ctx._parent.message.guild.id
            channel_id = ctx._parent.message.channel.id

        if author_id:
            dest_lang = await self.language_of(author_id)
        if not dest_lang and channel_id:
            dest_lang = await self.language_of(channel_id)
        if not dest_lang and guild_id:
            dest_lang = await self.language_of(guild_id)
        return dest_lang

    async def language_of(self, snowflake: Snowflake) -> Optional[Language]:
        """
        Resolves a destination language for a snowflake.
        """
        return None


class DetectionAgent:
    delim = "\u200b"

    @staticmethod
    def encode_lang_str(s: str, lang: Language):
        """
        Append the language code into the string with a delimiter.
        """
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
            return DetectionAgent.delim.join(content), Language.from_code(lang_id)


class Translator:
    antecedent = GoogleTranslator()

    def __init__(self) -> None:
        """
        A simple wrapper around `googletrans.Translator` to allow the usage
        of Language enum elements as source and destination lang
        parameters.
        """

    def translate(self, payload: str, dest_lang: Language, src_lang: Language):
        """
        Translates text from source language to destination language.
        """
        return self.antecedent.translate(
            payload, dest=dest_lang.code, src=src_lang.code
        ).text


class TranslationAgent:
    def __init__(self, dest_lang: Language, translator: Translator) -> None:
        self.dest_lang = dest_lang
        self.translator = translator

    def translate(self, content: str):
        """
        Tokenizes the source string into segments to translate individually
        for better accuracy.
        """
        return self.trans_assemble(*self.tokenize(content), dest_lang=self.dest_lang)

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
        return payload, tokens

    def trans_assemble(
        self,
        payload: str,
        tokens: List[Dict[str, Any]],
        dest_lang: Optional[Language] = None,
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
            proper = tk["phrase"]
            if dest_lang:
                proper = self.translator.translate(
                    proper.strip().lower(), dest_lang=dest_lang, src_lang=src_lang
                )
            new_str[tk["start_pos"] + mitigate : tk["end_pos"] + mitigate] = proper
            if tk["end_pos"] - tk["start_pos"] <= len(proper):
                mitigate += len(proper) - (tk["end_pos"] - tk["start_pos"])
        return "".join(new_str)

    @staticmethod
    def clean_string(tokens: List[Dict[str, Any]]):
        return " ".join(tk["phrase"] for tk in tokens)
