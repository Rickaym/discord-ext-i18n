from typing import Any, Callable, Dict, Optional, Union, Coroutine
from discord import Interaction, Webhook
from discord.types.snowflake import Snowflake
from discord.enums import ComponentType
from discord.abc import Messageable
from discord.message import Message
from discord.http import HTTPClient
from discord.interactions import InteractionResponse
from discord.webhook.async_ import AsyncWebhookAdapter, WebhookMessage
from discord.ext.i18n.language import LANG_CODE2NAME, Language
from discord.ext.i18n.preprocess import (
    Detector,
    TranslationAgent,
    Translator,
)
from discord.ui import Modal

Messageable_send = Messageable.send
Message_edit = Message.edit
HTTPClient_edit_message = HTTPClient.edit_message
HTTPClient_send_message = HTTPClient.send_message
InteractionResponse_send_message = InteractionResponse.send_message
InteractionResponse_edit_message = InteractionResponse.edit_message
InteractionResponse_send_modal = InteractionResponse.send_modal
AsyncWebhookAdapter_create_interaction_response = (
    AsyncWebhookAdapter.create_interaction_response
)
AsyncWebhookAdapter_execute_webhook = AsyncWebhookAdapter.execute_webhook
Webhook_send = Webhook.send
WebhookMessage_edit = WebhookMessage.edit

InterfaceOverridable = Callable[
    ..., Coroutine[Any, Any, Union[Message, Interaction, None]]
]


async def try_defer(obj: Any):
    if isinstance(obj, InteractionResponse):
        if not obj.is_done():
            await obj.defer()
            return True
    return False


def wrap_i18n_editer(edit_func: InterfaceOverridable):
    """
    Returns a wrapped edit function that appends a language suffix into the
    content field as an entry point to the translation system.
    """

    async def wrapped_i18n_edit(self: Union[Message, InteractionResponse], **kwds):
        dest_lang = await Agent.detector.first_language_of(self)
        if dest_lang:
            kwds["content"] = Agent.encode_lang_str(
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
        content, lang = Agent.decode_lang_str(fields["content"])
        if lang:
            fields, fields["content"] = Agent.translate_payload(lang, fields, content)
    return HTTPClient_edit_message(self, channel_id, message_id, **fields)


def wrap_i18n_sender(send_func: InterfaceOverridable):
    """
    Returns a wrapped message sending function that appends a language suffix
    into the content field as an entry point to the translation system.
    """

    async def wrapped_i18n_send(
        self: Union[Messageable, InteractionResponse], content=None, *_, **kwds
    ):
        dest_lang = await Agent.detector.first_language_of(self)
        if dest_lang:
            content = Agent.encode_lang_str(content, dest_lang)
            if await try_defer(self):
                return await self._parent.followup.send(content, **kwds)
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
        payload, lang = Agent.decode_lang_str(content)
        if lang:
            kwds, content = Agent.translate_payload(lang, kwds, payload)
    return HTTPClient_send_message(self, channel_id, content, **kwds)


def i18n_Adapter_create_interaction_response(self: AsyncWebhookAdapter, *args, **kwds):
    """
    An override for `AsyncWebhookAdapter.create_interaction_response` whereby
    extracting language encoding if it exists and translates accordingly.
    """
    if kwds["data"] and ("content" in kwds["data"] or "title" in kwds["data"]):
        content_type = "content" if "content" in kwds["data"] else "title"
        content, lang = Agent.decode_lang_str(kwds["data"][content_type])

        if lang:
            kwds["data"], kwds["data"][content_type] = Agent.translate_payload(
                lang, kwds["data"], content
            )
    return AsyncWebhookAdapter_create_interaction_response(self, *args, **kwds)


def i18n_AsyncWebhookAdapter_execute_webhook(self: AsyncWebhookAdapter, *args, **kwds):
    if "payload" in kwds and kwds["payload"]:
        if "content" in kwds["payload"] and kwds["payload"]["content"].strip():
            content, lang = Agent.decode_lang_str(kwds["payload"]["content"])
            if lang:
                kwds["payload"], kwds["payload"]["content"] = Agent.translate_payload(
                    lang, kwds["payload"], content
                )
    return AsyncWebhookAdapter_execute_webhook(self, *args, **kwds)


async def i18n_InteractionResponse_send_modal(self: InteractionResponse, modal: Modal):
    """
    Language code is appended to the modal title if there is a language
    preference.

    TODO: Very problematic if translation functions are slow, often ends up
    timing out on responses.
    """
    dest_lang = await Agent.detector.first_language_of(self)
    if dest_lang:
        modal.title = Agent.encode_lang_str(modal.title, dest_lang)
    return await InteractionResponse_send_modal(self, modal)


class Agent:
    translator = Translator()
    detector = Detector()

    delim = "\u200b"
    translate_messages = True
    translate_embeds = False
    translate_buttons = False
    translate_selects = False
    translate_modals = False
    source_lang = Language.English
    _instantiated = False

    def __init__(
        self,
        translator: Optional[Translator] = None,
        detector: Optional[Detector] = None,
        translate_all: Optional[bool] = None,
        translate_messages: Optional[bool] = None,
        translate_embeds: Optional[bool] = None,
        translate_buttons: Optional[bool] = None,
        translate_selects: Optional[bool] = None,
        translate_modals: Optional[bool] = None,
        source_lang: Optional[Language] = None,
        handle_webhooks: bool = True,
    ):
        """
        Sets initialized injectors to override high and low level.
        At any given case, you cannot initialize this class more than
        once.

        ### Parameters:
            translate_x = enable translation for x
                defaults to: True for `translate_messages` and False for else
            source_lang = the language in which text is written in the bot
                defaults to: `Language.English`
            handle_webhooks = enable webhook translations (this is not a
            static property and is only settable through params)
        """
        if Agent._instantiated:
            raise TypeError("this class should only be instantiated once")
        else:
            Agent._instantiated = True

        setattr(
            AsyncWebhookAdapter,
            "create_interaction_response",
            i18n_Adapter_create_interaction_response,
        )
        setattr(
            AsyncWebhookAdapter,
            "execute_webhook",
            i18n_AsyncWebhookAdapter_execute_webhook,
        )
        if handle_webhooks:
            setattr(Webhook, "send", wrap_i18n_sender(Webhook_send))
        setattr(Messageable, "send", wrap_i18n_sender(Messageable_send))
        setattr(
            InteractionResponse,
            "send_message",
            wrap_i18n_sender(InteractionResponse_send_message),
        )
        setattr(HTTPClient, "send_message", i18n_HTTPClient_send_message)
        setattr(Message, "edit", wrap_i18n_editer(Message_edit))
        setattr(
            InteractionResponse,
            "edit_message",
            wrap_i18n_editer(InteractionResponse_edit_message),
        )
        setattr(WebhookMessage, "edit", wrap_i18n_editer(WebhookMessage_edit))
        setattr(HTTPClient, "edit_message", i18n_HTTPClient_edit_message)
        setattr(InteractionResponse, "send_modal", i18n_InteractionResponse_send_modal)

        for key, val in {
            "translator": translator,
            "detector": detector,
            "translate_messages": translate_messages,
            "translate_embeds": translate_embeds,
            "translate_buttons": translate_buttons,
            "translate_selects": translate_selects,
            "translate_modals": translate_modals,
            "source_lang": source_lang,
        }.items():
            if translate_all and key.startswith("translate_"):
                setattr(Agent, key, True)
            elif val is not None:
                setattr(Agent, key, val)

    @staticmethod
    def translate_components():
        return (
            Agent.translate_buttons or Agent.translate_selects or Agent.translate_modals
        )

    @staticmethod
    def translate_payload(
        lang: Language, payload: Dict[str, Any], content: Optional[str]
    ):
        """
        Translates a payload JSON object about to be sent to it's corresponding
        discord API Endpoint.

        Returns (Payload, Content)
        """
        agent = TranslationAgent(Agent.source_lang, lang, translator=Agent.translator)
        if Agent.translate_messages:
            if content:
                content = agent.translate(content)

        if Agent.translate_embeds:
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
                            if field["name"].strip() and field["name"] != "\u200b":
                                field["name"] = agent.translate(field["name"])
                            if field["value"].strip() and field["value"] != "\u200b":
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

        if (
            Agent.translate_components()
            and "components" in payload
            and payload["components"]
        ):
            if "title" in payload:
                payload["title"] = agent.translate(payload["title"])
            for i, template_row in enumerate(payload["components"]):
                if template_row:
                    row = template_row.copy()

                    for item in row["components"]:
                        if (
                            Agent.translate_buttons
                            and item["type"] == ComponentType.button.value
                        ):
                            if item["label"]:
                                item["label"] = agent.translate(item["label"])
                        elif (
                            Agent.translate_selects
                            and item["type"] == ComponentType.select.value
                        ):
                            if "placeholder" in item and item["placeholder"]:
                                item["placeholder"] = agent.translate(
                                    item["placeholder"]
                                )
                            for opt in item["options"]:
                                opt["label"] = agent.translate(opt["label"])
                        elif (
                            Agent.translate_modals
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
    def encode_lang_str(s: str, lang: Language):
        """
        Append the language code into the string with a delimiter.
        """
        same_lang = False
        if s:
            same_lang = Translator.antecedent.detect(s).lang == lang.code

        if not same_lang and lang is not Agent.source_lang:
            return f"{s or ''}{Agent.delim}{lang.code}"
        else:
            return s

    @staticmethod
    def decode_lang_str(s: str):
        """
        Extract the language code from a string if it exists.
        """
        *content, lang_id = s.split(Agent.delim)
        if lang_id not in LANG_CODE2NAME.keys():
            return s, None
        else:
            return Agent.delim.join(content) or None, Language.from_code(lang_id)
