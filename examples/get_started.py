from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector

intents = Intents.default()
# not necessary for the extension, enabled for msg commands
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}
bot.agent = Agent(translate_all=True)  # This must be instantiated at least and only once


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    """
    This decorated function will be called internally to get Language
    preferences.
    """
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    lang = Language.from_code(lang_code)
    if lang is None:
        return await ctx.reply("Bad language code!")
    else:
        # Set a language preference to the current channel.
        bot.preferences[ctx.channel.id] = lang
        await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    # This will be translated before sent if necessary
    await ctx.reply("Hey!!")


bot.run("TOKEN")
