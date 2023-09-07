from typing import Optional
from discord import Intents, Bot, ApplicationContext
from discord.ext.i18n import AutoI18nAgent, Language, Detector

intents = Intents.default()
# not necessary for the extension, enabled for msg commands
intents.messages = True
intents.message_content = True

bot = Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}
bot.agent = AutoI18nAgent(
    translate_all=True
)  # This must be instantiated at least and only once


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    """
    This decorated function will be called internally to get Language
    preferences.
    """
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


@bot.command(name="hi")
async def greet(ctx):
    # This will be translated before sent if necessary
    await ctx.reply("Hey!!")


bot.run("TOKEN")
