# An I18J extension for [discord.py](https://github.com/Rapptz/discord.py) (& forks)

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

```py
from typing import Optional
from discord.ext import commands
from discord import Intents

from discord.ext.i18n import Agent, Language

bot = commands.Bot(
    prefix="!",
    exts=...,
    intents=Intents.default(),
)

bot.agent = Agent()
bot.lang_preferences = {}


async def get_language_of(id: int) -> Optional[Language]:
    """
    This method will be called to determine whether if translation is
    necessary whenever the bot initiates an interface level request.

    Parameters:
        A snowflake ID which could either be; author id, channel id
        and guild id.

    Returns:
        None or the `Language` tied to this ID.
    """
    return bot.language_preferences[id]

bot.agent.set_lang_getter(get_language_of)

@commands.command(name="lang")
async def set_lang(ctx, lang_id):
    # ALlow language settings per-user basis
    bot.lang_preferences[ctx.author.id] = lang_id
    await ctx.reply(f"Set to {lang_id}. Try `!hi`.")

@commands.command(name="hi")
async def greet(ctx):
    """
    Replies with a "Hey!!" message translated to the preferential
    language automatically.
    """
    await ctx.reply("Hey!!")

bot.run(...)
```
