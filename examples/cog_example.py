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
bot.agent = Agent(translate_all=True)


class SomeCog(commands.Cog, Detector):
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

    @commands.command(name="lang")
    async def set_lang(self, ctx, lang_code):
        lang = Language.from_code(lang_code)
        if lang is None:
            return await ctx.reply("Bad language code!")
        else:
            self.preferences[ctx.channel.id] = lang
            await ctx.reply(
                f"I've set the language to `{lang.name.title()}` {lang.emoji}!"
            )

    @commands.command(name="hi")
    async def greet(self, ctx):
        await ctx.reply("Hey!!")


bot.add_cog(SomeCog(bot))

bot.run("TOKEN")
