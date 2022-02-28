import re
import logging
import os
import itertools
from argostranslate import package, translate
from .util import *
from bellingbot.util import env

log = logging.getLogger(__name__)

MODEL_DIR = env('TRANSLATION_MODEL_DIR')
LANG_PATTERN = re.compile(r'^(\w+)?(?:->(\w+))?$')

log.info("loading argos translation models...")
loaded_count = 0
for root, _, files in os.walk(MODEL_DIR):
    for filename in files:
        if filename.endswith('.argosmodel'):
            fullpath = os.path.join(root, filename)
            package.install_from_path(fullpath)
            log.debug(f"installed argos package: {fullpath}")
            loaded_count += 1
log.info(f"loaded {loaded_count} argos translation models")

installed_languages = dict(
    itertools.chain(
        ((str(lang).lower(), lang) for lang in translate.get_installed_languages()),
        ((str(lang.code).lower(), lang) for lang in translate.get_installed_languages())
    )
)

@handler
@alias('t', 'tr', 'trans')
@helpvars(supported_languages=', '.join(installed_languages.keys()))
@allow_from(GUILD)
async def translate(message: discord.Message, lang, *_, raw=None):
    """Translate a message or an ad-hoc string between languages
    usage: `translate language->language [string]`

    Translates a message or an ad-hoc string between languages.

    There are two ways to use the translator:

    - Mention me and say `translate from->to some text to translate`,
      where `from` and `to` are languages (see below).

    - Reply to another message you'd like to translate, mention me
      and say `translate from->to` (without any additional text).
      I'll translate the message you replied to, and respond to
      _that_ message with the translation.

    The `language->language` specifier also accepts a few different
    forms.

    - Specify `from->to` to translate `from` a language, `to` another language
    - Specify `->to` to translate from English, `to` another language
    - Specify just `from` to translate `from` a language, to English

    > Bellingcat's primary operating language is English, hence why there are
    > some English-centric shortcuts.

    Both spelled out languages as well as their international codes are
    accepted - for example, `en` and `english`, `es` and `spanish`, etc.
    Language names are not case sensitive.
    ---------------------------------------------------------------------------

    List of supported languages:
    ```
    {{supported_languages}}
    ```

    ---------------------------------------------------------------------------
    **Example:** to translate from English to Greek:
    ```
    @Bellingbot translate english->greek Hello, world!
    ```

    **Example:** to translate from English to Russian (using the shortcut):
    ```
    @Bellingbot ->ru Hello, world!
    ```

    **Example:** to translate from Ukrainian to English (using the shortcut):
    ```
    @Bellingbot uk Слава Україні!
    ```

    > **NOTE:** Translations are performed directly by the bot; text is not
    > sent to a third party service. There are no quotas, though keep in mind
    > translation quality might not necessarily be as high as dedicated
    > translation platforms.

    > Also keep in mind that, in some cases, an intermediary language is used
    > (a language that is first translated to, that is then further translated
    > to the destination language).

    > Bellingcat is not responsible for any errors the translator may make,
    > and provides no guarantees about the accuracy, cultural sensitivity,
    > or any other aspect of the translated text that may be perceived
    > as damaging or problematic. It is provided here as a convenience and
    > a tool. In cases where an accurate translation must be made, please
    > consult a professional translation service.
    """

    # Isolate any non-`lang` text
    raw = [*raw.split(None, 1), ''][1]

    reply_to = message

    if len(raw) == 0 and message.reference:
        refmsg = message.reference.resolved
        if isinstance(refmsg, discord.DeletedReferencedMessage):
            await message.reply("**(not a translation)** Sorry, I couldn't seem to find that message.")
            return False;

        raw = refmsg.content
        reply_to = refmsg

    if len(raw) == 0:
        await message.reply("**(not a translation)** Found nothing to translate")
        return False

    match = LANG_PATTERN.match(lang)
    if not match:
        await message.reply(f"**(not a translation)** Invalid language specifier `{lang}`. Try `help translate`.")
        return False

    fro, to = match.group(1, 2)
    if not fro:
        fro = 'en'
    if not to:
        to = 'en'

    fro = fro.lower()
    to = to.lower()

    fro_lang = installed_languages.get(fro, None)
    to_lang = installed_languages.get(to, None)

    if fro is None:
        await message.reply(f"**(not a translation)** Invalid source language `{fro}`. Try `help translate`.")
        return False
    if to is None:
        await message.reply(f"**(not a translation)** Invalid target language `{to}`. Try `help translate`.")
        return False

    translator = fro_lang.get_translation(to_lang)
    if translator is None:
        await message.reply(f"**(not a translation)** Sorry, I can't translate from **{fro_lang.name}** to **{to_lang.name}**. :disappointed:")
        return False

    log.info(f"translating {len(raw)} characters from {str(fro_lang)} to {str(to_lang)}")
    translated = translator.translate(raw)
    log.info(f"ok")

    destspec = ""
    if to_lang.code != "en":
        destspec = f" to {to_lang.name}"

    await reply_to.reply(f"**(translated from {fro_lang.name}{destspec})** {translated}")
    return True
