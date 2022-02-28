import discord
from bellingbot import util as botutil

all_handlers = dict()

GUILD = (1<<0)
DM = (1<<1)
def allow_from(which):
    def _wrap(fn):
        async def _inner(message, *args):
            is_dm = botutil.is_dm_channel(message.channel)
            is_guild = botutil.is_guild_channel(message.channel)

            allowed = ((((which & DM) == DM) and is_dm) or ((which & GUILD) == GUILD) and is_guild)

            if not allowed:
                return False

            await fn(message, *args)
            return True

        _inner.__name__ = fn.__name__
        _inner.__doc__ = fn.__doc__
        return _inner
    return _wrap


def alias(name1, *names):
    def _wrap(fn):
        for name in (name1, *names):
            if name in all_handlers:
                raise Exception(f"duplicate handler: {name}")
            all_handlers[name] = fn
        return fn
    return _wrap

def handler(fn):
    if fn.__name__ in all_handlers:
        raise Exception(f"duplicate handler: {fn.__name__}")
    async def _wrap(*args, **kwargs):
        r = await fn(*args, **kwargs)
        if r == None:
            r = True
        return r
    _wrap.__name__ = fn.__name__
    _wrap.__doc__ = fn.__doc__
    all_handlers[fn.__name__] = _wrap
