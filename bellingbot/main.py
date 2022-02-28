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
            args = None

            if botutil.is_dm_channel(message.channel):
                args = message.content.split()
                if len(args) > 0:
                    if args[0] == f"<@!{client.user.id}>":
                        args = args[1:]
                else:
                    args = None
            else:
                is_mentioned = any((m.id == client.user.id for m in message.mentions))
                if is_mentioned and message.content.startswith(f"<@!{client.user.id}>"):
                    args = message.content.split()[1:]

            if args is not None:
                if len(args) == 0:
                    args.append('help')

                handler = handlers.get(args[0], None)
                ok = False
                if handler:
                    ok = await handler(message, *args[1:])
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
