# An I18J extension for [discord.py](https://github.com/Rapptz/discord.py) and forks.

![GitHub](https://img.shields.io/github/license/Rickaym/discord-ext-i18n)
![Status](https://img.shields.io/badge/status-unreleased-red)

## Key Features

- Very minimal setup required
- Forward Compatiblity
- Facilitates for full control if needed

## Installing

This is not a standalone package, it is an extension for `discord.py` and it's corresponding hooks like `py-cord`. Therefore it is recommended that there exists an installation of `discord.py==2.0` or any equivalent forks.

To install this extension, run the following command:

```
# Linux/macOS
python3 -m pip install -U discord-ext-i18n

# Windows
py -3 -m pip install -U discord-ext-i18n
```

## Quick Example

**Required Steps**:
- Subclass the `discord.ext.i18n.preprocess.Detector` class to define your own language getter. (this getter is called with an ID of *users/guild/channel* to see if it has a language attached)
- Instantiate a `discord.ext.i18n.Agent` class to inject
- Make a command so that users can set preferences.

```py
from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language
from discord.ext.i18n.preprocess import Detector

intents = Intents.default()
# not necessary for the extension, enabled only for msg commands
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}


class LangDetector(Detector):
    async def language_of(self, id) -> Optional[Language]:
        """
        Override the function to define our own. Get language of a snowflake ID,
        return None by default.
        """
        return bot.preferences.get(id, None)


bot.agent = Agent(detector=LangDetector())


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    """
    Tie a language to the current channel.
    """
    lang = Language.from_code(lang_code)
    bot.preferences[ctx.channel.id] = lang
    await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    """
    Replies with "Hey!!" in the preferred language of the current channel.
    """
    await ctx.reply("Hey!!")


bot.run(...)
```
