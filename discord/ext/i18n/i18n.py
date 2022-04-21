import warnings

from typing import Any, Callable, Dict, List, Optional, Union, Coroutine
from discord import Interaction
from discord.types.snowflake import Snowflake
from discord.enums import ComponentType
from discord.abc import Messageable
from discord.message import Message
from discord.http import HTTPClient
from discord.interactions import InteractionResponse
from discord.webhook.async_ import AsyncWebhookAdapter, WebhookMessage
from discord.ext.i18n.cache import Cache
from discord.ext.i18n.language import Language
from discord.ext.i18n.preprocess import (
    DetectionAgent,
    Detector,
    TranslationAgent,
    Translator,
)

Messageable_send = Messageable.send
Message_edit = Message.edit
HTTPClient_edit_message = HTTPClient.edit_message
HTTPClient_send_message = HTTPClient.send_message
InteractionResponse_send_message = InteractionResponse.send_message
InteractionResponse_edit_message = InteractionResponse.edit_message
AsyncWebhookAdapter_create_interaction_response = (
    AsyncWebhookAdapter.create_interaction_response
)
WebhookMessage_edit = WebhookMessage.edit

InterfaceOverridable = Callable[
    ..., Coroutine[Any, Any, Union[Message, Interaction, None]]
]

"""
TODO: Improper translations when dealing with send_message requests
      Specific string caching is not working properly
      Components are being translated twice
"""


def translate_payload(
    lang: Language,
    payload: Dict[str, Any],
    content: Optional[str]
):
    """
    Translates a payload JSON object about to be sent to it's corresponding
    discord API Endpoint.
    """
    agent = TranslationAgent(lang, translator=Agent.translator)
    if content:
        content = agent.translate(content)

    if "embeds" in payload and payload["embeds"]:
        embeds = payload["embeds"]
    else:
        embeds = []

    if "embed" in payload:
        embeds.append(payload["embed"])

    for i, template_embed in enumerate(embeds):
        if template_embed:
            embed = template_embed.copy()
            if "fields" in embed:
                for field in embed["fields"]:
                    if field["name"].strip() and field["name"] != "\u200b":
                        field["name"] = agent.translate(field["name"])
                    if field["value"].strip() and field["value"] != "\u200b":
                        field["value"] = agent.translate(field["value"])

            if (
                "author" in embed
                and "name" in embed["author"]
                and embed["author"]["name"].strip()
            ):
                embed["author"]["name"] = agent.translate(embed["author"]["name"])

            if (
                "footer" in embed
                and "text" in embed["footer"]
                and embed["footer"]["text"].strip()
            ):
                embed["footer"]["text"] = agent.translate(embed["footer"]["text"])

            if "description" in embed and embed["description"].strip():
                embed["description"] = agent.translate(embed["description"])

            if "title" in embed and embed["title"].strip():
                embed["title"] = agent.translate(embed["title"])
            embeds[i] = embed

    if "components" in payload and payload["components"]:
        for i, template_row in enumerate(payload["components"]):
            if template_row:
                row = template_row.copy()
                for item in row["components"]:
                    if item["type"] is ComponentType.button.value:
                        if item["label"]:
                            item["label"] = agent.translate(item["label"])
                payload["components"][i] = row

    return payload, content


def predicate_i18n_edit(edit_func: InterfaceOverridable):
    """
    Returns a wrapped edit function that appends a language suffix into the
    content field as an entry point to the translation system.
    """

    async def wrapped_i18n_edit(
        self: Union[Message, InteractionResponse], **kwds
    ) -> Message:
        dest_lang = await Agent.detector.first_language_of(self)
        if dest_lang:
            kwds["content"] = DetectionAgent.encode_lang_str(
                kwds.get("content", None) or "", dest_lang
            )
        return await edit_func(self, **kwds)

    return wrapped_i18n_edit


def i18n_HTTPClient_edit_message(
    self: HTTPClient, channel_id: Snowflake, message_id: Snowflake, **fields: Any
):
    """
    An override for `HTTPClient.edit_message` whereas it extracts extra
    language data if exists and translates accordingly.

    Language data is only appended when the recieving channel has affiliations
    with a guild.
    """
    if fields["content"]:
        content, lang = DetectionAgent.decode_lang_str(fields["content"])
        if lang:
            fields, fields["content"] = translate_payload(
                lang, fields, "".join(content)
            )
    return HTTPClient_edit_message(self, channel_id, message_id, **fields)


def predicate_i18n_send(send_func: InterfaceOverridable):
    """
    Returns a wrapped message sending function that appends a language suffix
    into the content field as an entry point to the translation system.
    """

    async def wrapped_i18n_send(
        self: Union[Messageable, InteractionResponse], content=None, *_, **kwds
    ):
        dest_lang = await Agent.detector.first_language_of(self)
        if dest_lang:
            content = DetectionAgent.encode_lang_str(content, dest_lang)
        return await send_func(self, content, **kwds)

    return wrapped_i18n_send


def i18n_HTTPClient_send_message(
    self: HTTPClient,
    channel_id: Snowflake,
    content: Optional[str],
    *_,
    **kwds,
):
    """
    Intercepts the excess language suffix from the content field if it exists
    and performs translation.
    """
    if content:
        payload, lang = DetectionAgent.decode_lang_str(content)
        if lang:
            kwds, content = translate_payload(lang, kwds, "".join(payload))
    return HTTPClient_send_message(self, channel_id, content, **kwds)


def i18n_Adapter_create_interaction_response(self: AsyncWebhookAdapter, *args, **kwds):
    """
    An override for `AsyncWebhookAdapter.create_interaction_response` whereas it
    extracts extra language data if exists and translates accordingly.

    Language data is only appended when the recieving channel has affiliations
    with a guild.
    """
    if kwds["data"] and "content" in kwds["data"]:
        content, lang = DetectionAgent.decode_lang_str(kwds["data"]["content"])
        if lang:
            kwds["data"], kwds["data"]["content"] = translate_payload(
                lang, kwds["data"], "".join(content)
            )
    return AsyncWebhookAdapter_create_interaction_response(self, *args, **kwds)


class NotImplementedWarning(UserWarning):
    ...


class Agent:
    translator = Translator()
    detector = Detector()

    def __init__(
        self,
        translator: Optional[Translator] = None,
        detector: Optional[Detector] = None
    ):
        """
        Sets initialized injectors to override necessary high and low level
        methods that implements the bot interface.
        At any given time, there can only be one translator or a detector,
        therefore, instantiating more `Agent` classes will override any
        installed detector and translator.

        ### Injections
        Surround your text with `\\u200b` to prevent being translated.
        This is a zero-width character and it will not affect your message
        output in any way even if you removed uninstalled `discord-ext-i18n`.

        E.g. `\\u200b`report`\\u200b` can be used to avoid reperations!

        Interfaces Affected Includes:
            - message sending/reply/edit/respond
            - views and button components
            - selects and modals

        Methods Affected methods Includes:
            - AsyncWebhookAdapter.create_interaction_response
            - Messegable.send
            - InteractionResponse.send_message
            - HTTPClient.send_message
            - Message.edit
            - InteractionResponse.edit_message
            - WebhookMessage.edit
            - HTTPClient.edit_message
        """
        setattr(
            AsyncWebhookAdapter,
            "create_interaction_response",
            i18n_Adapter_create_interaction_response,
        )

        setattr(
            Messageable,
            "send",
            predicate_i18n_send(Messageable_send)
        )
        setattr(
            InteractionResponse,
            "send_message",
            predicate_i18n_send(InteractionResponse_send_message),
        )
        setattr(
            HTTPClient,
            "send_message",
            i18n_HTTPClient_send_message
        )
        setattr(
            Message,
            "edit",
            predicate_i18n_edit(Message_edit)
        )
        setattr(
            InteractionResponse,
            "edit_message",
            predicate_i18n_edit(InteractionResponse_edit_message),
        )
        setattr(
            WebhookMessage,
            "edit",
            predicate_i18n_edit(WebhookMessage_edit)
        )
        setattr(
            HTTPClient,
            "edit_message",
            i18n_HTTPClient_edit_message
        )

        if translator:
            Agent.translator = translator
        if detector:
            if detector.language_of is Agent.detector.language_of:
                warnings.warn(
                    "You forgot to implement the `language_of` function!",
                    NotImplementedWarning
                    )
            Agent.detector = detector

    def precache(self, src: str, lang_list: List[Language]):
        ag = TranslationAgent(lang_list)
        # CONTINUE HERE
