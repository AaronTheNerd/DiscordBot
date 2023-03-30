"""A module for the miscellaneous cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
import discord
import randfacts
from discord import app_commands
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, BindingConfig
from utils.error import on_error


class MiscCog(BoundCog):
    def __init__(self, bot: commands.Bot, binding: BindingConfig) -> None:
        super().__init__(bot, binding)

    @app_commands.command(name="hello", description="Hello World!")
    async def _hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Hello, {interaction.user}!")

    @app_commands.command(name="fact", description="Gives a random fact.")
    async def _fact(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Did you know?\n{randfacts.get_fact()}"
        )

    @app_commands.command(name="ping", description="Ping!")
    async def _ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.pong()

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await on_error(ctx, error, self.bot)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        MiscCog(bot, CONFIGS.cogs.misc.binding, **CONFIGS.cogs.misc.kwargs),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
