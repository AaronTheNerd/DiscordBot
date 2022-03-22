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

from config import DISCORD_CONFIGS, MISC_COG_CONFIGS, SPOTIFY_COG_CONFIGS, EVENTS_COG_CONFIGS, YOUTUBE_COG_CONFIGS, DND_COG_CONFIGS, PLANK_COG_CONFIGS

from cogs.dnd_cog import DnDCog
from cogs.events_cog import EventsCog
from cogs.misc_cog import MiscCog
from cogs.spotify_cog import SpotifyCog
from cogs.youtube_cog import Music

bot = commands.Bot(command_prefix=DISCORD_CONFIGS["command_prefix"], case_insensitive=DISCORD_CONFIGS["case_insensitive"])

if MISC_COG_CONFIGS["enabled"]:
    bot.add_cog(MiscCog(bot))

if SPOTIFY_COG_CONFIGS["enabled"]:
    bot.add_cog(SpotifyCog(bot))

if EVENTS_COG_CONFIGS["enabled"]:
    bot.add_cog(EventsCog(bot))

if YOUTUBE_COG_CONFIGS["enabled"]:
    bot.add_cog(Music(bot))

if DND_COG_CONFIGS["enabled"]:
    bot.add_cog(DnDCog())

if __name__ == "__main__":
    bot.run(DISCORD_CONFIGS["token"])
