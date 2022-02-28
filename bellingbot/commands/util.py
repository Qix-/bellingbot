import discord
import re
from bellingbot import util as botutil
from inspect import cleandoc, signature, Parameter

all_handlers = dict()

GUILD = (1<<0)
DM = (1<<1)
TEMPLATE_VAR_PATTERN = re.compile(r'\{\{(\w+)\}\}')

# Since you can't actually subscript range with `inf` from the math
# package, we fake it here.
INFINITY = 99999999999999
PROBABLY_INFINITY = INFINITY // 10
is_inf = lambda v: v >= PROBABLY_INFINITY

class Handler(object):
    def __init__(self, fn):
        self._fn = fn

        sig = signature(fn)
        params = [*sig.parameters.values()]
        assert len(params) > 0, "handler must accept at least a 'message' parameter"
        assert params[0].name == 'message', "first handler parameter must be named 'message'"

        self.send_raw = any((p.name == 'raw' for p in params))
        assert (not self.send_raw or params[-1].name == 'raw'), "if handler specifies 'raw', it must come last"

        self.send_max = (
            INFINITY
            if any((p.kind == Parameter.VAR_POSITIONAL for p in params))
            else sum(
                (
                    1 if (
                        p.kind == Parameter.POSITIONAL_OR_KEYWORD
                        or p.kind == Parameter.POSITIONAL_ONLY
                    )
                    else 0
                    for p in params
                )
            )
        ) - 1 - (1 if self.send_raw else 0) # subtract `message` and `raw`

        self.send_min = (
            sum((1 if p.kind != p.VAR_POSITIONAL and p.default == Parameter.empty else 0 for p in params[1:(self.send_max+1)]))
        )

        self.name = fn.__name__
        fulldoc = cleandoc(fn.__doc__)
        self.short_doc, self.doc = fulldoc.split('\n', 1)
        self.allowed = GUILD | DM
        self.aliases = set()

    def substitute_help_vars(self, **kwargs):
        self.short_doc = TEMPLATE_VAR_PATTERN.sub(lambda m: kwargs.get(m.group(1), m.group(1)), self.short_doc)
        self.doc = TEMPLATE_VAR_PATTERN.sub(lambda m: kwargs.get(m.group(1), m.group(1)), self.doc)

    async def __call__(self, message: discord.Message, args, raw):
        is_dm = botutil.is_dm_channel(message.channel)
        is_guild = botutil.is_guild_channel(message.channel)

        allowed = (
            (((self.allowed & DM) == DM) and is_dm)
            or ((self.allowed & GUILD) == GUILD) and is_guild
        )

        if not allowed:
            return False

        if len(args) < self.send_min or len(args) > self.send_max:
            argspec = (
                f"exactly **{self.send_min}**"
                if (self.send_min == self.send_max)
                else (
                    f"at least **{self.send_min}**"
                    if is_inf(self.send_max)
                    else f"between **{self.send_min}** and **{self.send_max}**"
                )
            )
            await message.author.send(
                f"invalid arguments for `{self.name}`; got **{len(args)}**, expected {argspec}. Try `help {self.name}` for more info."
            )
            return False

        kwargs = dict()
        if self.send_raw:
            kwargs['raw'] = raw

        v = await self._fn(message, *args, **kwargs)
        if v == None:
            v = False
        return v

def allow_from(which):
    def _wrap(fn):
        if not isinstance(fn, Handler):
            fn = Handler(fn)
        fn.allowed = which
        return fn
    return _wrap


def alias(name1, *names):
    def _wrap(fn):
        if not isinstance(fn, Handler):
            fn = Handler(fn)
        for name in (name1, *names):
            if name in all_handlers:
                raise Exception(f"duplicate handler: {name}")
            all_handlers[name] = fn
            fn.aliases.add(name)
        return fn
    return _wrap


def helpvars(**kwargs):
    def _wrap(fn):
        if not isinstance(fn, Handler):
            fn = Handler(fn)
        fn.substitute_help_vars(**kwargs)
        return fn
    return _wrap


def handler(fn):
    if not isinstance(fn, Handler):
        fn = Handler(fn)
    if fn.name in all_handlers:
        raise Exception(f"duplicate handler: {fn.name}")
    all_handlers[fn.name] = fn
