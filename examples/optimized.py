from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector
from random import randint

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
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
        await ctx.reply(
            f"I've set the language to `{lang.name.title()}` \u200b{lang.emoji}!"
        )


@bot.command(name="rand")
async def rand_num(ctx):
    """
    Replies with a random number.

    In this example, we can estimate that this string can be translated in
    100 ways based on the random results of the number.
    This could affect the speed negatively.

    In this case we can wrap the variable fragment of the string with
    \u200b or zero width unicode characters that tells the translator to skip
    the phrase.
    """
    await ctx.reply(f"Your random number is \u200b{randint(0, 100)}\u200b!")


bot.run("TOKEN")
