from inspect import getfullargspec
from typing import Any, Callable, Optional, Union, Coroutine
from discord import Interaction, Webhook
from discord.types.snowflake import Snowflake
from discord.abc import Messageable
from discord.message import Message
from discord.http import HTTPClient
from discord.interactions import InteractionResponse
from discord.webhook.async_ import AsyncWebhookAdapter, WebhookMessage
from discord.ui import Modal

from discord.ext.i18n.language import Language
from discord.ext.i18n.preprocess import (
    TranslationAgent,
    Translator,
)

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
            kwds["content"] = TranslationAgent.encode_lang_str(
                Agent.source_lang, kwds.get("content", None) or "", dest_lang
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
        content, lang = TranslationAgent.decode_lang_str(fields["content"])
        if lang:
            fields, fields["content"] = TranslationAgent.translate_payload(
                lang, fields, content, **Agent.translate_config()
            )
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
            content = TranslationAgent.encode_lang_str(
                Agent.source_lang, content, dest_lang
            )
            if await try_defer(self):
                return await self._parent.followup.send(content, **kwds)  # type: ignore
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
        payload, lang = TranslationAgent.decode_lang_str(content)
        if lang:
            kwds, content = TranslationAgent.translate_payload(
                lang, kwds, payload, **Agent.translate_config()
            )
    return HTTPClient_send_message(self, channel_id, content, **kwds)


def i18n_Adapter_create_interaction_response(self: AsyncWebhookAdapter, *args, **kwds):
    """
    An override for `AsyncWebhookAdapter.create_interaction_response` whereby
    extracting language encoding if it exists and translates accordingly.
    """
    if kwds["data"] and ("content" in kwds["data"] or "title" in kwds["data"]):
        content_type = "content" if "content" in kwds["data"] else "title"
        content, lang = TranslationAgent.decode_lang_str(kwds["data"][content_type])

        if lang:
            (
                kwds["data"],
                kwds["data"][content_type],
            ) = TranslationAgent.translate_payload(
                lang, kwds["data"], content, **Agent.translate_config()
            )
    return AsyncWebhookAdapter_create_interaction_response(self, *args, **kwds)


def i18n_AsyncWebhookAdapter_execute_webhook(self: AsyncWebhookAdapter, *args, **kwds):
    if "payload" in kwds and kwds["payload"]:
        if "content" in kwds["payload"] and kwds["payload"]["content"].strip():
            content, lang = TranslationAgent.decode_lang_str(kwds["payload"]["content"])
            if lang:
                (
                    kwds["payload"],
                    kwds["payload"]["content"],
                ) = TranslationAgent.translate_payload(
                    lang, kwds["payload"], content, **Agent.translate_config()
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
        modal.title = TranslationAgent.encode_lang_str(
            Agent.source_lang, modal.title, dest_lang
        )
    return await InteractionResponse_send_modal(self, modal)


def isinstancemethod(func: Callable) -> bool:
    """
    Returns whether if a given function is a staticmethod or an
    instancemethod/classmethod.
    """
    return "self" in getfullargspec(func)[0]


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


class AgentSession:
    def __init__(
        self,
        translate_all: Optional[bool] = None,
        translate_messages: Optional[bool] = None,
        translate_embeds: Optional[bool] = None,
        translate_buttons: Optional[bool] = None,
        translate_selects: Optional[bool] = None,
        translate_modals: Optional[bool] = None,
        source_lang: Optional[Language] = None,
    ):
        """
        A context menu to temporarily reconfigure the translation settings until
        it has been exited.

        ### Parameters:
            translate_x = temporarily enable translation for x

            source_lang = the language in which text is written in the bot
                defaults to: whichever language is set to `Agent.source_lang`

        E.g.
        ```py
        with AgentSession(translate_embeds=False):
            await ctx.reply(
                embed=Embed(
                    title="Theoretical Physics",
                    description="This description will never be translated.",
                )
            )
        ```
        The is basically equivalent to:
        ```py
        DEFAULT = Agent.translate_embeds
        Agent.translate_embeds = False
        await ctx.reply(
            embed=Embed(
                title="Theoretical Physics",
                description="This description will never be translated.",
            )
        )
        Agent.translate_embeds = DEFAULT
        ```
        """

        vmap = {
            "translate_messages": translate_messages,
            "translate_embeds": translate_embeds,
            "translate_buttons": translate_buttons,
            "translate_selects": translate_selects,
            "translate_modals": translate_modals,
            "source_lang": source_lang,
        }
        self.prior = {key: getattr(Agent, key, None) for key in vmap}

        for key, val in vmap.items():
            if translate_all and key.startswith("translate_"):
                setattr(Agent, key, True)
            elif val is not None:
                setattr(Agent, key, val)

    def __enter__(self):
        return self

    def __exit__(self, *arg, **kwds):
        for key, val in self.prior.items():
            if val is not None:
                setattr(Agent, key, val)


class Agent:
    translator = Translator()
    detector = Detector()

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
    def translate_config():
        """
        Returns a dictionary of configurations needed to run down a payload
        translation.
        """
        return {
            "source_lang": Agent.source_lang,
            "translator": Agent.translator,
            "translate_components": (
                Agent.translate_buttons
                or Agent.translate_selects
                or Agent.translate_modals
            ),
            "translate_messages": Agent.translate_messages,
            "translate_embeds": Agent.translate_embeds,
            "translate_buttons": Agent.translate_buttons,
            "translate_selects": Agent.translate_selects,
            "translate_modals": Agent.translate_modals,
        }
