from os import getenv
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

bot.agent = Agent()


class SomeCog(commands.Cog, Detector):
    """
    A `language_getter` defined inside a cog must be subclassed under
    `Detector`, this is entirely compatible with a cog.
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.preferences = {}
        self.bot = bot

    @Detector.language_getter
    async def get_lang(self, id) -> Optional[Language]:
        """
        Override the function to define our own. Get language of a snowflake
        ID, return None by default.
        """
        return self.preferences.get(id, None)

    @commands.command(name="lang")
    async def set_lang(self, ctx, lang_code):
        """
        Tie a language to the current channel.
        """
        lang = Language.from_code(lang_code)
        self.preferences[ctx.channel.id] = lang
        await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")

    @commands.command(name="hi")
    async def greet(self, ctx):
        """
        Replies with "Hey!!" in the preferred language of the current channel.
        """
        await ctx.reply("Hey!!")


bot.add_cog(SomeCog(bot))

bot.run(...)
