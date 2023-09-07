from typing import Optional
from discord import Intents, Bot, ApplicationContext
from discord.ext.i18n import AutoI18nAgent, Language, Detector, no_translate
from random import randint

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = Bot(
    command_prefix="!",
    intents=intents,
)
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


@bot.slash_command(name="rand")
async def rand_num(ctx: ApplicationContext):
    """
    Replies with a random number.

    In this example, the string can be translated in a hundred different ways
    based on the random result. This will affect the speed negatively. In order
    to avoid this, we can use the no_translate function to tell the translator
    to skip the phrase.
    """
    await ctx.respond(f"Your random number is {no_translate(randint(0, 100))}!")


bot.run("TOKEN")
