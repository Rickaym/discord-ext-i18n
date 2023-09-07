from typing import Optional
from discord import Embed, Intents, ApplicationContext, Bot, Option
from discord.ext.i18n import AutoI18nAgent, Language, Detector, AgentSession, no_translate

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}

# The "AutoI18nAgent" class has static flags to decide whether if it should translate
# a given object: AutoI18nAgent.translate_messages, AutoI18nAgent.translate_selects
#
# For ease of access, you can set these flags when
# instantiating the class like below.
bot.agent = AutoI18nAgent(
    translate_selects=True, translate_all=True  # just set everything else to true also
)

# You may also change these flags outside like below by setting it to the class
# NOT INSTANCES as these flags are static
AutoI18nAgent.translate_buttons = False
AutoI18nAgent.translate_embeds = False


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


@bot.slash_command(name="set")
async def set_translation_flag(
    ctx: ApplicationContext,
    option: Option(str, choices=["messages", "embeds", "buttons", "selects", "modals"]),
    state: str,
):
    """
    Toggle translation for interfaces.
    """
    if state not in ("True", "False"):
        return await ctx.respond(f"{no_translate(f'`{state}`')} is not a valid state.")
    else:
        await ctx.respond("Changing state!")

    state = False if state == "False" else True

    if option == "messages":
        AutoI18nAgent.translate_messages = state
    elif option == "embeds":
        AutoI18nAgent.translate_embeds = state
    elif option == "buttons":
        AutoI18nAgent.translate_buttons = state
    elif option == "selects":
        AutoI18nAgent.translate_selects = state
    elif option == "modals":
        AutoI18nAgent.translate_modals = state


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
    # DEFAULT = AutoI18nAgent.translate_embeds
    # AutoI18nAgent.translate_embeds = False
    # await ctx.reply(
    #     embed=Embed(
    #         title="Theoretical Physics",
    #         description="This description will never be translated.",
    #     )
    # )
    # AutoI18nAgent.translate_embeds = DEFAULT


bot.run("TOKEN")
