"""Written by Aaron Barge
Copyright 2021

Module for any intializations needed for the discord bot
"""

from discord.ext import commands

from config import DISCORD_CONFIGS, MISC_COG_CONFIGS, SPOTIFY_COG_CONFIGS, EVENTS_COG_CONFIGS

from misc_cog import MiscCog
from spotify_cog import SpotifyCog
from events_cog import EventsCog

bot = commands.Bot(command_prefix=DISCORD_CONFIGS["command_prefix"])

if MISC_COG_CONFIGS["enabled"]:
    bot.add_cog(MiscCog(bot))

if SPOTIFY_COG_CONFIGS["enabled"]:
    bot.add_cog(SpotifyCog(bot))

if EVENTS_COG_CONFIGS["enabled"]:
    bot.add_cog(EventsCog(bot))

if __name__ == "__main__":
    bot.run(DISCORD_CONFIGS["token"])