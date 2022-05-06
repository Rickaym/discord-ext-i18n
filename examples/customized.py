from typing import List, Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector, Translator


intents = Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)


class OtherTranslator(Translator):
    def translate(self, payload: str, dest_lang: Language, src_lang: Language):
        """
        This function must be overriden.
        """
        # Translates every word as "Banana" lol
        return "Banana"

    def batch_translate(
        self, payloads: List[str], dest_lang: Language, src_lang: Language
    ):
        """
        Optionally implementable - by default calls the translate function on
        each string passed.
        """
        return super().batch_translate(payloads, dest_lang, src_lang)


bot.preferences = {}
bot.agent = Agent(translator=OtherTranslator(), translate_all=True)


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


@bot.command(name="hi")
async def greet(ctx):
    await ctx.reply("Hey!!")


bot.run("TOKEN")
