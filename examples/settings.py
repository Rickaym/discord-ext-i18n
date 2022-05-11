from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}

# The "Agent" class has static flags to decide whether if it should translate
# a given object: Agent.translate_messages, Agent.translate_selects
#
# For ease of access, you can set these flags when
# instantiating the class like below.
bot.agent = Agent(
    translate_selects=True,
    translate_all=True  # just set everything else to true also
)

# You may also change these flags outside like below by setting it to the class
# NOT INSTANCES as these flags are static
Agent.translate_buttons = False
Agent.translate_embeds = False


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    lang = Language.from_code(lang_code)
    if lang is None:
        return await ctx.reply("Bad language code!")
    elif lang is Language.English:
        if ctx.channel.id in bot.preferences:
            bot.preferences.pop(ctx.channel.id)
    else:
        bot.preferences[ctx.channel.id] = lang

    await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="set")
async def trans_setting(ctx, option, state):
    """
    Turn on and off translation features for given
    interfaces through a command.
    """
    if state not in ("True", "False"):
        return await ctx.reply(f"\u200b`{state}`\u200b is not a valid state.")

    state = False if state == "False" else True
    if option == "messages":
        Agent.translate_messages = state
    elif option == "embeds":
        Agent.translate_embeds = state
    elif option == "buttons":
        Agent.translate_buttons = state
    elif option == "selects":
        Agent.translate_selects = state
    elif option == "modals":
        Agent.translate_modals = state


bot.run("TOKEN")
