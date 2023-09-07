from traceback import print_exception
from googletrans import Translator as GoogleTranslator
from typing import Any, Dict, List, Optional
from enum import Enum
from string import ascii_letters, punctuation, whitespace

from .cache import Cache
from .language import CODEBLOCK_LANGS, LANG_CODE2NAME, Language

punctuation += f"{whitespace}\u200b"
trailing_punctuation = punctuation.replace("?", "")


class ComponentType(Enum):
    action_row = 1
    button = 2
    select = 3
    input_text = 4


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
    delim = "\u200b"
    decoratives = {
        "`": "`",
        "```": "```",
        "*": "*",
        "**": "**",
        "_": "_",
        "<@": ">",
        "<#": ">",
        "<@&": ">",
        "<!@": ">",
        "<:": ">",
        "(": ")",
        delim: delim,
    }
    # Add all possible entries codeblock starters
    decoratives.update({f"```{lang}\n": "```" for lang in CODEBLOCK_LANGS})
    ignored = {"<@", "<#", "<@&", "<!@", "<:", delim}
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
    def translate_payload(
        dest_lang: Language,
        payload: Dict[str, Any],
        content: Optional[str],
        *,
        source_lang: Language,
        translator: Translator,
        translate_messages: bool,
        translate_embeds: bool,
        translate_buttons: bool,
        translate_selects: bool,
        translate_modals: bool,
        translate_components: bool,
    ):
        """
        Shortcut to instantiating a TranslationAgent object and translating
        dictionary fields.

        Translates a payload JSON object about to be sent to it's corresponding
        discord API Endpoint.

        Returns (Payload, Content)
        """
        agent = TranslationAgent(source_lang, dest_lang, translator=translator)
        if translate_messages:
            if content:
                content = agent.translate(content)

        if translate_embeds:
            if "embeds" in payload and payload["embeds"]:
                embeds = payload["embeds"]
            else:
                embeds = []

            if "embed" in payload and payload["embed"]:
                embeds.append(payload["embed"])

            for i, template_embed in enumerate(embeds):
                if template_embed:
                    embed = template_embed.copy()
                    if "fields" in embed:
                        for field in embed["fields"]:
                            if field["name"].strip() and field["name"] != TranslationAgent.delim:
                                field["name"] = agent.translate(field["name"])
                            if field["value"].strip() and field["value"] != TranslationAgent.delim:
                                field["value"] = agent.translate(field["value"])

                    if (
                        "author" in embed
                        and "name" in embed["author"]
                        and embed["author"]["name"].strip()
                    ):
                        embed["author"]["name"] = agent.translate(
                            embed["author"]["name"]
                        )

                    if (
                        "footer" in embed
                        and "text" in embed["footer"]
                        and embed["footer"]["text"].strip()
                    ):
                        embed["footer"]["text"] = agent.translate(
                            embed["footer"]["text"]
                        )

                    if "description" in embed and embed["description"].strip():
                        embed["description"] = agent.translate(embed["description"])

                    if "title" in embed and embed["title"].strip():
                        embed["title"] = agent.translate(embed["title"])
                    embeds[i] = embed

            if len(embeds) > 1:
                payload["embeds"] = embeds
            elif len(embeds) == 1:
                payload["embed"] = embeds[0]

        if translate_components and "components" in payload and payload["components"]:
            if "title" in payload:
                payload["title"] = agent.translate(payload["title"])
            for i, template_row in enumerate(payload["components"]):
                if template_row:
                    row = template_row.copy()

                    for item in row["components"]:
                        if (
                            translate_buttons
                            and item["type"] == ComponentType.button.value
                        ):
                            if item["label"]:
                                item["label"] = agent.translate(item["label"])
                        elif (
                            translate_selects
                            and item["type"] == ComponentType.select.value
                        ):
                            if "placeholder" in item and item["placeholder"]:
                                item["placeholder"] = agent.translate(
                                    item["placeholder"]
                                )
                            for opt in item["options"]:
                                opt["label"] = agent.translate(opt["label"])
                        elif (
                            translate_modals
                            and item["type"] == ComponentType.input_text.value
                        ):
                            if item["label"]:
                                item["label"] = agent.translate(item["label"])
                            if "placeholder" in item and item["placeholder"]:
                                item["placeholder"] = agent.translate(
                                    item["placeholder"]
                                )
                            if "value" in item and item["value"]:
                                item["value"] = agent.translate(item["value"])

                    payload["components"][i] = row

        return payload, content

    @staticmethod
    def encode_lang_str(source_lang: Language, s: str, dest_lang: Language):
        """
        Append the language code into the string with a delimiter.
        """
        same_lang = False
        if s:
            same_lang = Translator.antecedent.detect(s).lang == dest_lang.code  # type: ignore

        if not same_lang and dest_lang is not source_lang:
            return f"{s or ''}{TranslationAgent.delim}{dest_lang.code}"
        else:
            return s

    @staticmethod
    def decode_lang_str(s: str):
        """
        Extract the language code from a string if it exists.
        """
        *content, lang_id = s.split(TranslationAgent.delim)
        if lang_id not in LANG_CODE2NAME.keys():
            return s, None
        else:
            return TranslationAgent.delim.join(content) or None, Language.from_code(lang_id)

    @staticmethod
    def similar_decors(char: str):
        return list(
            filter(lambda decor: decor.startswith(char), TranslationAgent.decoratives)
        )

    @staticmethod
    def tokenize(string: str):
        """
        Create "tokens" from a general string.

        The process of tokenization is limited to single iteration of
        the string in one single flow. The tokenizer will
        add any substantive character into the stack if the stack is empty.
        When it meets any decoratives, it will conclude the token there
        thus removing the initial character from the stack, and then
        adding on the new decorative in. Each decorative has another decorative
        that concludes it. I.e. if we start a string with '**', we won't make a
        new token unless there are more decoratives nested or we find an instance
        of '**' again.
        """
        stack, tokens = [], []
        i = 0

        def generate_token(end_char: str = ""):
            """
            encouter: a decorative that invoked token generation
            """
            if not stack:
                return

            last_char = stack.pop(-1)
            start, end = last_char["pos"], i
            if end_char in TranslationAgent.decoratives:
                # tokens generated when a starting decorative is
                # hit needs to remove it's end number from consuming the
                # decorative
                end -= len(end_char) - 1

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
                tokens.append({"start_pos": start, "end_pos": end, "phrase": phrase})

        string_len = len(string)
        while i < string_len:
            char = string[i]

            if char not in ascii_letters:
                tmp_char = char
                tmp_pos = int(i)
                sample = TranslationAgent.similar_decors(char)
                while sample and i + 1 != string_len:
                    i += 1
                    char += string[i]
                    sample = TranslationAgent.similar_decors(char)

                # loop oversteps one character if not EOF
                if i + 1 != string_len:
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
            elif (
                char in TranslationAgent.decoratives
                or char in TranslationAgent.decoratives.values()
            ):
                generate_token(char)
                # post is incremented by one since when making a token
                # we expect the starting position from one after the
                # decorative
                stack.append({"char": char, "pos": char_pos + 1})
            elif not stack and char.strip():
                # stack is empty = start a new token
                stack.append({"char": char, "pos": char_pos})
            i += 1

        if stack and stack[-1]["char"] not in TranslationAgent.ignored:
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

            new_str[tk["start_pos"] + mitigate: tk["end_pos"] + mitigate] = phrase
            if tk["end_pos"] - tk["start_pos"] != len(phrase):
                mitigate += len(phrase) - (tk["end_pos"] - tk["start_pos"])
        return "".join(new_str)
