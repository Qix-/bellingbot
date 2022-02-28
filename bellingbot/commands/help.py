import re
from .util import *

SPACER = 12
SPLIT_PATTERN = re.compile(r'^-{5,}$', re.M)

@handler
@alias('hello', 'hi', '👋')
@allow_from(GUILD | DM)
async def help(message: discord.Message, name=None):
    """Show a list of commands, or more information about a specific command
    Usage: `help` or `help some-command`

    Shows the main help documentation, or when given the name of a command
    shows more help for that command.
    """

    if name:
        handler = all_handlers.get(name)
        if handler is None:
            text = f"Unknown command **{name}** - try just `help` by itself for a list of all bot commands"
            return False
        else:
            text = f"**{handler.name}**\n{handler.doc}"
    else:
        text = cleandoc(f"""Hi there :wave: I'm the **Bellingcat** bot.
            It looks like you've asked me for some help.

            The help command, by itself, shows this message - a list of available commands.
            To learn more about a specific command, you can message me `help some-command`.
            Many commands can also be sent to me via direct message.

            List of commands:
            ```""")

        for pair in all_handlers.items():
            name = pair[0]
            handler = pair[1]
            if name is not handler.name:
                # it's an alias; ignore
                continue
            spacer = ' ' * (SPACER - len(name))
            text += f"\n{name}{spacer}{handler.short_doc}"

        text += '\n```'

    for page in SPLIT_PATTERN.split(text):
        await message.author.send(page)

    return True
