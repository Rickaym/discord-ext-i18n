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
bot.agent = Agent()  # THIS MUST BE INSTANTIATED!


@Detector.language_getter
async def get_lang(id: int) -> Optional[Language]:
    """
    Set a language getter that gets the preferred
    language from a bot dict by ID if it exists.
    """
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    """
    A simple command to set a language preference to the current channel.
    """
    lang = Language.from_code(lang_code)
    bot.preferences[ctx.channel.id] = lang
    await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    """
    Replies with "Hey!!" in the preferred language of
    the current channel. No code change here.
    """
    await ctx.reply("Hey!!")


bot.run(...)
