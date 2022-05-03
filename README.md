# An automatic string translation extension for [PyCord](https://github.com/Pycord-Development/pycord)

![GitHub](https://img.shields.io/github/license/Rickaym/discord-ext-i18n)
[![Coverage Status](https://coveralls.io/repos/github/Rickaym/discord-ext-i18n/badge.svg?branch=master)](https://coveralls.io/github/Rickaym/discord-ext-i18n?branch=master)

## Key Features

- Automatic string translation with no code changes
- Cached translations with garbage collection
- Cog incorporability
- Fully customizable
- Forward Compatible

In essence, this extension will translate all
specified objects [here](#coverage) into any registered language
depending on the preferences of the channel or guild that the object
is getting sent to. It will be very helpful to go through this short [FAQ](#features-extended--faq).

## Installing

This is an extension for `PyCord`. It is recommended that there exists an installation of `py-cord>=2.0.0b5`.

To install this extension, run the following command:

```
# Linux/macOS
python3 -m pip install -U discord-ext-i18n

# Windows
py -3 -m pip install -U discord-ext-i18n
```

## Quick Example

**Required Steps**:
- Subclass the `discord.ext.i18n.preprocess.Detector` class to define your own language getter. (this getter is called with an ID of *guilds / channels* to see if it has a language preference)
- Instantiate a `discord.ext.i18n.Agent` class to inject
- Make a command so that users can set preferences.

```py
from typing import Optional
from discord.ext import commands
from discord import Intents
from discord.ext.i18n import Agent, Language, Detector

intents = Intents.default()
# not necessary for the extension, enabled for msg commands
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}
bot.agent = Agent()  # THIS MUST BE INSTANTIATED!


@Detector.language_getter
async def get_lang(id: int) -> Optional[Language]:
    """
    Set a language getter that gets the preferred
    language from a bot dict by ID if it exists.
    """
    return bot.preferences.get(id, None)


@bot.command(name="lang")
async def set_lang(ctx, lang_code):
    """
    A simple command to set a language preference to the current channel.
    """
    lang = Language.from_code(lang_code)
    bot.preferences[ctx.channel.id] = lang
    await ctx.reply(f"I've set the language to `{lang.name.title()}` {lang.emoji}!")


@bot.command(name="hi")
async def greet(ctx):
    """
    Replies with "Hey!!" in the preferred language of
    the current channel. No code change here.
    """
    await ctx.reply("Hey!!")


bot.run(...)
```

## Features Extended & FAQ

1. [How do we tell the extension to translate x?](#how-do-we-tell-the-extension-to-translate-x)
2. [How does the extension work?](#how-does-the-extension-work)
3. [What does it use to translate the string?](#what-does-it-use-to-translate-the-string)
4. [When are strings not translated?](#when-are-strings-not-translated)

### How do we tell the extension to translate x?
Simply put, it translates everything given [here](#coverage). This means
that you will need to explicitly specify if translation is not needed in certain
strings.

Apart from that, you can call the usual methods like `Messegable.send`,
`ApplicationContext.respond` with your texts and the translation will be
gracefully handled in the backend. Absolutely
no code change is necessary when calling these high-level methods. Check out the many examples to see specific cases.

### How does the extension work?
As an overview; when you call high-level methods such as `Messegable.send`
the extension intercepts the text and destination it's being sent to. It resolves
whether if this text requires translation by calling the language getter with the
ID of the destination and if it does, it will append
the language code into the content field. This inscription is later intercepted
before it gets sent to the discord API where tokenization, translation, caching
and other book-keeping occurs if necessary.

### What does it use to translate the string?
By default, the extension translates your strings using the [Google Translator](https://pypi.org/project/googletrans/)
library. You can override this with your own translator like in the example
[here](./examples/modified_translator.py).


### When are strings not translated?
Obviously, the strings will not be translated if they're either already in
the language preferred by the destination or the destination has no preference.

### Coverage
- `Messages`
- `Interaction Messages`
- `Embeds`
- `Views`
- `Modals`.
