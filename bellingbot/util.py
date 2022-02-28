import discord

def is_dm_channel(channel: discord.ChannelType):
    return isinstance(channel, discord.DMChannel) or isinstance(channel, discord.GroupChannel)

def is_guild_channel(channel: discord.ChannelType):
    return isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread)

def env(name, default = None):
    import os
    v = os.getenv(name, default)
    if v is None:
        raise Exception(f"missing required environment variable: {name}")
    return v
