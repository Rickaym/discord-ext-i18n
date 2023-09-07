from os import getenv
from typing import Optional
from discord import (
    Color,
    Embed,
    Intents,
    Interaction,
    SelectOption,
    ApplicationContext,
    Option,
    Bot,
)
from random import randint

from functools import partial

from dotenv import load_dotenv
from discord.ext.i18n import (
    AutoI18nAgent,
    Language,
    Detector,
    AgentSession,
    no_translate,
)
from discord.enums import InputTextStyle
from discord.ui import View, Button, Modal, Select
from discord.ui.input_text import InputText


intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents)
bot.preferences = {}
bot.agent = AutoI18nAgent(translate_all=True)


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    return bot.preferences.get(id, None)


@bot.slash_command(name="lang")
async def set_lang(ctx: ApplicationContext, lang_code: str):
    """
    Set the language for the bot in the current channel.
    """
    lang = Language.from_code(lang_code)
    if lang is None:
        return await ctx.respond("Bad language code!")
    elif lang is Language.English:
        if ctx.channel.id in bot.preferences:
            bot.preferences.pop(ctx.channel.id)
    else:
        bot.preferences[ctx.channel.id] = lang

    await ctx.respond(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.slash_command(name="set")
async def set_translation_flag(
    ctx: ApplicationContext,
    option: Option(str, choices=["messages", "embeds", "buttons", "selects", "modals"]),
    state: str,
):
    """
    Toggle translation for interfaces.
    """
    if state not in ("True", "False"):
        return await ctx.respond(f"{no_translate(f'`{state}`')} is not a valid state.")
    else:
        await ctx.respond("Changing state!")

    state = False if state == "False" else True

    if option == "messages":
        AutoI18nAgent.translate_messages = state
    elif option == "embeds":
        AutoI18nAgent.translate_embeds = state
    elif option == "buttons":
        AutoI18nAgent.translate_buttons = state
    elif option == "selects":
        AutoI18nAgent.translate_selects = state
    elif option == "modals":
        AutoI18nAgent.translate_modals = state


@bot.slash_command(name="rand")
async def rand_num(ctx: ApplicationContext):
    await ctx.respond(f"Your random number is {no_translate(randint(0, 100))}!")


@bot.command(name="hi")
async def greet(ctx):
    await ctx.reply("Hey!!")


@bot.slash_command(name="s-hi")
async def slash_greet(ctx):
    await ctx.respond("Hey!!")


async def create_embed(channel_id):
    return (
        Embed(
            title=f"What is {no_translate('`discord-ext-i18n`')}?",
            description="It is a program that does automatic translations with"
            " no code change necessary for the bot.",
            color=Color.random(),
        )
        .set_footer(text=f"\u200bLanguage: {await get_lang(channel_id)}")
        .set_author(name="Help Menu")
    )


@bot.command(name="embed")
async def embed(ctx):
    await ctx.reply(embed=await create_embed(ctx.channel.id))


@bot.slash_command(name="s-embed")
async def slash_embed(ctx):
    await ctx.respond(embed=await create_embed(ctx.channel.id))


@bot.command(name="embeds")
async def embeds(ctx):
    await ctx.reply(
        embeds=[await create_embed(ctx.channel.id), await create_embed(ctx.channel.id)]
    )


@bot.slash_command(name="s-embeds")
async def slash_embeds(ctx):
    await ctx.respond(
        embeds=[await create_embed(ctx.channel.id), await create_embed(ctx.channel.id)]
    )


def create_view():
    v = View()

    async def butt_callback(self: Button, int: Interaction):
        await int.response.send_message(self.label)

    buttons = [
        Button(label="Yes"),
        Button(label="No"),
        Button(label=no_translate("Very Good")),
    ]
    for butt in buttons:
        butt.callback = partial(butt_callback, butt)
        v.add_item(butt)

    v.add_item(
        Select(
            placeholder="What fruit do humans eat?",
            options=[
                SelectOption(label="Apple"),
                SelectOption(
                    label=no_translate("Orange")
                ),  # won't translate this either
                SelectOption(label="Banana"),
            ],
        )
    )
    return v


@bot.command(name="view")
async def view(ctx):
    await ctx.reply("Are you a human being?", view=create_view())


@bot.slash_command(name="s-view")
async def slash_view(ctx):
    await ctx.respond("Are you a human being?", view=create_view())


class MyModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Short Input", placeholder="Placeholder Test"))
        self.add_item(
            InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=InputTextStyle.long,
            )
        )

    async def callback(self, interaction):
        await interaction.response.send_message(
            embed=Embed(title="Modal Results", color=Color.random())
            .add_field(name="First Input", value=self.children[0].value, inline=False)
            .add_field(name="Second Input", value=self.children[1].value, inline=False)
        )


@bot.slash_command(name="modal")
async def slash_modal(ctx):
    await ctx.send_modal(MyModal(title="Input Form"))


@bot.command(name="selective")
async def selective(ctx):
    with AgentSession(translate_embeds=False):
        await ctx.reply(
            embed=Embed(
                title="Theoretical Physics",
                description="This description will never be translated.",
            )
        )


load_dotenv()
bot.run(getenv("TOKEN"))
