from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector

intents = Intents.default()
# not necessary for the extension, enabled only for msg commands
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}

# Translate before the bot starts and pull into cache
bot.agent = Agent(
    precache_dict={
        "Hey!!": [Language.Indonesian, Language.Myanmar],
        "I've set the language to ": [Language.Indonesian, Language.Myanmar],
    }
)


@Detector.language_getter
async def get_lang(id) -> Optional[Language]:
    """
    Override the function to define our own. Get language of a snowflake ID,
    return None by default.
    """
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    """
    Tie a language to the current channel.
    """
    lang = Language.from_code(lang_code)
    bot.preferences[ctx.channel.id] = lang
    await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    """
    Replies with "Hey!!" in the preferred language of the current channel.
    """
    await ctx.reply("Hey!!")


bot.run(...)
