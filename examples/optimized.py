from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector
from random import randint

intents = Intents.default()
# not necessary for the extension, enabled for msg commands
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}
bot.agent = Agent()


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
    await ctx.reply(
        f"I've set the language to `{lang.name.title()}` \u200b{lang.emoji}\u200b!"
    )


@bot.command(name="rand")
async def rand_num(ctx):
    """
    Replies with a random number.
    """
    # In this example, we can estimate that this string can be translated in
    # up to 100 ways based on the random results of the number.
    # This can sometimes be unintended as it also bogs down in speed.
    # In this case we can wrap the variable fragment of the string with
    # \u200b or zero width unicode characters that tells the translator to skip
    # this while tokenizing.
    await ctx.reply(f"Your random number is \u200b{randint(0, 100)}\u200b!")


bot.run(...)
