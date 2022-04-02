"""Written by Aaron Barge
Copyright 2021

Module for any intializations needed for the discord bot.
Permissions:
    Text:
        Send Messages
        Embed Links
        Add Reactions
    Voice:
        Connect
        Speak
        Use Voice Activity
    General:
        Manage Roles
        Manage Channels
        View Channels
Permission Integer: 305155152
"""

from discord.ext import commands

from src.configs import CONFIGS

from cogs.dnd_cog import DnDCog
from cogs.events_cog import EventsCog
from cogs.misc_cog import MiscCog
from cogs.youtube_cog import Music

bot = commands.Bot(
    command_prefix=CONFIGS.command_prefix,
    case_insensitive=CONFIGS.case_insensitive
)

if CONFIGS.cogs["misc"].enabled:
    bot.add_cog(MiscCog(bot))

bot.add_cog(EventsCog(bot))

if CONFIGS.cogs["youtube"].enabled:
    bot.add_cog(Music(bot))

if CONFIGS.cogs["dnd"].enabled:
    bot.add_cog(DnDCog())

if __name__ == "__main__":
    bot.run(CONFIGS.token)
