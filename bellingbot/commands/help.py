from inspect import cleandoc
from .util import *

SPACER = 12

@handler
@alias('hello', 'hi', '👋')
@allow_from(GUILD | DM)
async def help(msg: discord.Message, name = None, *_):
    """Shows a list of commands, or more information about a specific command
    Usage: `help` or `help some-command`

    Shows the main help documentation, or when given the name of a command
    shows more help for that command.
    """

    if name:
        handler = all_handlers.get(name)
        if handler is None:
            text = f"Unknown command **{name}** - try just `help` by itself for a list of all bot commands"
        else:
            text = f"**{handler.__name__}**"
            text += cleandoc(handler.__doc__).split('\n', 1)[1]
    else:
        text = cleandoc(f"""Hi there :wave: I'm the **Bellingcat** bot.
            It looks like you've asked me for some help.

            The help command, by itself, shows this message -
            a list of available commands.

            To learn more about a specific command, you can
            message me `help some-command`.

            List of commands:
            ```""")

        for pair in all_handlers.items():
            name = pair[0]
            handler = pair[1]
            if name is not handler.__name__:
                # it's an alias; ignore
                continue
            spacer = ' ' * (SPACER - len(name))
            doc = handler.__doc__.split('\n', 1)[0]
            text += f"\n{name}{spacer}{doc}"

        text += '\n```'

    await msg.author.send(text)
