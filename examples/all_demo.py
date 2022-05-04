from typing import Optional
from discord.ext import commands
from discord import (
    ApplicationContext,
    Color,
    Embed,
    Intents,
    SelectOption,
    slash_command,
)
from discord.ext.i18n import Agent, Language, Detector
from discord.enums import InputTextStyle
from discord.ui import View, Button, Modal, Select
from discord.ui.input_text import InputText

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!", intents=intents, debug_guilds=[805782778473611315]
)
bot.preferences = {}
bot.agent = Agent(translate_all=True)


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    lang = Language.from_code(lang_code)
    if lang is None:
        return await ctx.reply("Bad language code!")
    else:
        bot.preferences[ctx.channel.id] = lang
        await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    await ctx.reply("Hey!!")


@slash_command(name="hi")
async def slash_greet(ctx):
    await ctx.respond("Hey!!")


async def create_embed(channel_id):
    return (
        Embed(
            title="What is \u200b`discord-ext-i18n`\u200b?",
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


@slash_command(name="embed")
async def slash_embed(ctx):
    await ctx.respond(embed=await create_embed(ctx.channel.id))


def create_view():
    v = View()
    v.add_item(Button(label="Yes"))
    v.add_item(Button(label="No"))
    v.add_item(Button(label="\u200bVery Good"))
    v.add_item(
        Select(
            placeholder="What fruit do humans eat?",
            options=[
                SelectOption(label="Apple"),
                SelectOption(label="Orange"),
                SelectOption(label="Banana"),
            ],
        )
    )
    return v


@bot.command(name="view")
async def view(ctx):
    await ctx.reply("Are you a human being?", view=create_view())


@slash_command(name="view")
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


@bot.message_command(name="modal")
async def modal(ctx, msg):
    await ctx.send_modal(MyModal(title="Input Form"))


@slash_command(name="modal")
async def slash_modal(ctx):
    await ctx.send_modal(MyModal(title="Input Form"))


bot.run(...)
