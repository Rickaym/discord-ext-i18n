from typing import Optional
from discord.ext import commands
from discord import Embed, Intents
from discord.ext.i18n import Agent, Language, Detector
from discord.ext.i18n.agent import AgentSession

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
    translate_selects=True, translate_all=True  # just set everything else to true also
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
    Enable or disable translation features for given
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


@bot.command(name="selective")
async def selective(ctx):
    # We put our messaging code into the `AgentSession` -- which is a context
    # manager that handles temporary translation settings I.e. translation
    # settings set here gets reverted when the context manager exits.
    #
    # Here we enforce the extension to NOT translate this embed no matter
    # what settings we have prior. This is the only way to do occurance
    # selective translation so far.
    with AgentSession(translate_embeds=False):
        await ctx.reply(
            embed=Embed(
                title="Theoretical Physics",
                description="This description will never be translated.",
            )
        )

    # The code above is rougly equivalent to
    #
    # DEFAULT = Agent.translate_embeds
    # Agent.translate_embeds = False
    # await ctx.reply(
    #     embed=Embed(
    #         title="Theoretical Physics",
    #         description="This description will never be translated.",
    #     )
    # )
    # Agent.translate_embeds = DEFAULT


bot.run("TOKEN")
