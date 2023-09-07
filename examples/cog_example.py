from typing import Optional
from discord import Intents, Bot, Cog, commands, ApplicationContext
from discord.ext.i18n import AutoI18nAgent, Language, Detector

intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = Bot(
    command_prefix="!",
    intents=intents,
)
bot.agent = AutoI18nAgent(translate_all=True)


class SomeCog(Cog, Detector):
    """
    A language getter defined inside a cog must be subclassed under Detector.
    (compatible with a cog).
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.preferences = {}
        self.bot = bot

    @Detector.lang_getter
    async def get_lang(self, id) -> Optional[Language]:
        return self.preferences.get(id, None)

    @commands.slash_command(name="lang")
    async def set_lang(self, ctx: ApplicationContext, lang_code: str):
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

        await ctx.respond(
            f"I've set the language to `{lang.name.title()}` {lang.emoji}!"
        )

    @commands.command(name="hi")
    async def greet(self, ctx):
        await ctx.reply("Hey!!")


bot.add_cog(SomeCog(bot))

bot.run("TOKEN")
