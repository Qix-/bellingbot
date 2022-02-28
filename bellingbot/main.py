# Important that this goes first.
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

import asyncio
import discord

from . import util as botutil

log = logging.getLogger(__name__)

def env(name, default = None):
    import os
    v = os.getenv(name, default)
    if v is None:
        raise Exception(f"missing required environment variable: {name}")
    return v

async def amain():
    log.info("starting the Bellingcat bot")

    DISCORD_TOKEN = env('DISCORD_TOKEN')
    DISCORD_APP_ID = env('DISCORD_APP_ID')

    from .commands import handlers
    print(handlers)

    intents = discord.Intents()
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True
    intents.dm_messages = True
    intents.dm_reactions = True

    client = discord.Client(
        loop = asyncio.get_event_loop(),
        application_id = DISCORD_APP_ID,
        intents = intents
    )

    @client.event
    async def on_ready():
        log.info(f"logged in as {client.user.name}#{client.user.discriminator}")

    @client.event
    async def on_message(message):
        if message.author.id == client.user.id:
            return;

        try:
            content_string = None
            me_tag = f"<@!{client.user.id}>"

            if botutil.is_dm_channel(message.channel):
                content_string = message.content
                if content_string.startswith(me_tag):
                    content_string = content_string[len(me_tag):]
            else:
                is_mentioned = any((m.id == client.user.id for m in message.mentions))
                if is_mentioned and message.content.startswith(me_tag):
                    content_string = message.content[len(me_tag):]

            if content_string is not None:
                args = content_string.split()

                if len(args) == 0:
                    args.append('help')
                    cmd = 'help'
                else:
                    split = content_string.split(None, 1)
                    cmd = split[0]
                    content_string = '' if len(split) < 2 else split[1]
                    args = args[1:]

                handler = handlers.get(cmd, None)

                ok = False
                if handler:
                    ok = await handler(message, args, raw=content_string)
                if not ok:
                    await message.add_reaction('❓')

        except Exception as exc:
            log.error("failed to handle message dispatch", exc_info=exc)

    await client.start(token = DISCORD_TOKEN, reconnect=True)

    while True:
        await asyncio.sleep(30)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain())
