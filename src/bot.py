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

import discord
from discord.ext import commands

from cogs.dnd import DnDCog
from cogs.events import EventsCog
from cogs.misc import MiscCog
from cogs.youtube import Music
from configs import CONFIGS


def main() -> None:

    intents = discord.Intents.default()
    intents.members = True
    
    bot = commands.Bot(command_prefix=CONFIGS.command_prefix, case_insensitive=CONFIGS.case_insensitive, intents=intents)

    if CONFIGS.cogs.misc.enabled:
        bot.add_cog(MiscCog(bot, **CONFIGS.cogs.misc.kwargs))

    if CONFIGS.cogs.events.enabled:
        bot.add_cog(EventsCog(bot, **CONFIGS.cogs.events.kwargs))

    if CONFIGS.cogs.youtube.enabled:
        bot.add_cog(Music(bot, **CONFIGS.cogs.youtube.kwargs))

    if CONFIGS.cogs.dnd.enabled:
        bot.add_cog(DnDCog(**CONFIGS.cogs.dnd.kwargs))

    bot.run(CONFIGS.token)

if __name__ == "__main__":
    main()
