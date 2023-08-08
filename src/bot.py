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

from configs import CONFIGS


class CustomBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=CONFIGS.command_prefix,
            intents=discord.Intents.all(),
            application_id=CONFIGS.app_id,
            case_insensitive=CONFIGS.case_insensitive,
            help_command=None,
        )
        self.remove_command("help")

    async def setup_hook(self) -> None:
        if CONFIGS.cogs.misc.enabled:
            await self.load_extension("cogs.misc")

        if CONFIGS.cogs.events.enabled:
            await self.load_extension("cogs.events")

        if CONFIGS.cogs.youtube.enabled:
            await self.load_extension("cogs.youtube")

        if CONFIGS.cogs.dnd.enabled:
            await self.load_extension("cogs.dnd")

        await bot.tree.sync(guild=discord.Object(id=CONFIGS.guild_id))

    async def on_ready(self) -> None:
        print(f"{self.user} has logged in")


bot = CustomBot()
bot.run(CONFIGS.token)
