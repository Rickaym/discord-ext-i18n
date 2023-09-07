# A [PyCord](https://github.com/Pycord-Development/pycord) extension for internationalization

<a href="https://discord.gg/UmnzdPgn6g"><img src="https://img.shields.io/badge/GET SUPPORT-DISCORD-orange?style=for-the-badge&logo=discord&logoColor=white&color=5865F2"></a>
<a href="https://github.com/Pycord-Development/pycord"><img src="https://img.shields.io/badge/Pycord-%3E=2.0.0b5-orange?style=for-the-badge&logo=python&logoColor=white"></a>
<a href="https://pypi.org/project/discord-ext-i18n"><img src="https://img.shields.io/pypi/v/discord-ext-i18n?style=for-the-badge&logo=pypi&logoColor=white&color=green"></a>

```diff
+ Note: `Agent` class has been renamed as `AutoI18nAgent` but the old name is still supported
```

## Key Features

- Automatic text translations for messages, embeds [etc..](#fields-covered-by-automatic-translation)
- Zero code change necessary
- Fully customizable
- Forward Compatible

The extension is able to automatically translate all
specified objects [here](#fields-covered-by-automatic-translation) into any registered language
depending on the preferences of the destination channel or guild.
For instance, if a channel has the preference for Spanish, any messages, embeds etc.. that are being sent to the channel will be automatically translated into Spanish before it is sent.

Translations will carry over markdown!

```diff
+ I've set the language to `English` 🏴󠁧󠁢󠁥󠁮󠁧󠁿!
+ He establecido el idioma en `Spanish` 🇪🇸!
+ ငါဘာသာစကားကိုထားတယ် `မြန်မာ (ဗမာ)` 🇲🇲!
```

_GoogleTranslated string in different languages with formatting maintained_

Check out the [FAQ](#faq), [Examples](#Examples) and [other feathers](#features-extended) for more information.
This extension is relatively new so please report any bugs at [issues](https://github.com/Rickaym/discord-ext-i18n/issues)!

## Fields Covered by Automatic Translation

- `Messages`
- `Interaction Messages`
- `Embeds`
- `Buttons`
- `Selects`
- `Modals` (beta)
- `Webhooks` (beta)

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

- Define a language getter function decorated with the `Detector.lang_getter` decorator
  (this getter is called with an ID of _guilds / channels_ to see if it has a
  language preference)
- Instantiate a `discord.ext.i18n.AutoI18nAgent` class to configure and inject code
- Create a command for users to set preferences

```py
from typing import Optional
from discord import Intents, Bot, ApplicationContext
from discord.ext.i18n import AutoI18nAgent, Language, Detector

intents = Intents.default()
# not necessary for the extension, enabled for msg commands
intents.messages = True
intents.message_content = True

bot = Bot(
    command_prefix="!",
    intents=intents,
)
bot.preferences = {}
bot.agent = AutoI18nAgent(
    translate_all=True
)  # This must be instantiated at least and only once


@Detector.lang_getter
async def get_lang(id) -> Optional[Language]:
    """
    This decorated function will be called internally to get Language
    preferences.
    """
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


@bot.command(name="hi")
async def greet(ctx):
    # This will be translated before sent if necessary
    await ctx.reply("Hey!!")


bot.run("TOKEN")
```

## Examples

1. [Get Started](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/get_started.py) - A minimal example on how to get started with the extension.
2. [Cog Example](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/cog_example.py) - Get started but inside a cog.
3. [Customized](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/customized.py) - An example on how to customize/make your own translator and override the default one.
4. [Settings](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/settings.py) - An example on how to enable/disable the extension from translating certain fields
5. [Optimized](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/optimized.py) - An example on how to ignore translation on parts of a string that is prone to change
6. [All Objects](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/all_objects.py) - A summary example of every object that is affected by translation + all features discussed prior

## Features Extended
### Tokenization

Tokenization breaks down a string in any order or magnitude of markdown decorations to the extent accepted by discord, into separate tokens to ready for batch translation. Once translated, the new phrases are reassembeled into correct positions and thus maintaining decorative characters fairly accurately.

### Constants
This library implements constants for:
1. Language `Names` *to* `Code` *to* `Emoji` enum

Examples:
```py
>>> Language.English.code
... en
>>> Language.English.emoji
... 🏴󠁧󠁢󠁥󠁮󠁧󠁿
>>> Language.name
... english
```
To access enum elements for a specific language through it's corresponding code or name:
```py
>>> Language.from_code("en")
... Language.English
>>> Language.from_name("english")
... Language.English
```

2. Codeblock identifiers

`CODEBLOCK_LANGS` is an exhaustive set of string identifiers that are considered valid code block languages in the tokenizer.

## FAQ
1. [How do we tell the extension to translate x?](#how-do-we-tell-the-extension-to-translate-x)
2. [How does the extension work?](#how-does-the-extension-work)
3. [What does it use to translate the string?](#what-does-it-use-to-translate-the-string)
4. [When are strings not translated?](#when-are-strings-not-translated)
5. [How do I avoid translation on specific function calls?](#how-do-i-avoid-translation-on-specific-function-calls)

### How do we tell the extension to translate x?

By default, the extension will translate all messages and ignore others. If you want
to translate other objects such as buttons, embeds and so on, you will have
to explicitly specify them as a parameter when instantiating the `AutoI18nAgent` class or modify the
`translate_x` flag from the class. See detailed example [here](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/settings.py)

Apart from that, you can call the usual methods like `Messegable.send`,
`ApplicationContext.respond` with your texts and the translation will be
handled in the backend. Absolutely
no code change is necessary when calling these high-level methods.

### How does the extension work?

When you call high-level methods e.g. `Messegable.send`
the extension intercepts the text and the destination it's being sent to. It resolves
whether if this text requires translation by calling the language getter with the
ID of its destination. If it has one, it will append
the language code into an appropriate field and this appendage is later extracted
before text gets sent to the discord API where tokenization, translation, caching
and other book-keeping occurs if necessary.

### What does it use to translate the string?

By default, the extension translates your strings using the [Google Translator](https://pypi.org/project/googletrans/)
library. You can override this with your own translator like in the example
[here](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/customized.py).

### When are strings not translated?

Strings are not translated in cases where either if the text are already
detected to be in the language
that it should be translated into, or the destination no preference.

### How do I avoid translation on specific function calls?

You can switch the flags to process specific call translations with some
code changes. One example is the command `selective` [here](https://github.com/Rickaym/discord-ext-i18n/blob/master/examples/settings.py).

---

#### TODO / KNOWN ISSUES

[-] Defer interaction responses only if translation doesn't exist in cache

[-] Resolve the issue with not being able to translate in time for `Modals` and they can't be deferred....

[-] Support translation in Webhooks

[-] More tests
