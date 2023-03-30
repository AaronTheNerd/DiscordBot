"""A module for the DnD cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
import random

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from configs import CONFIGS
from utils.error import on_error

DICE_CHOICES = [
    Choice(name="d4", value=4),
    Choice(name="d6", value=6),
    Choice(name="d8", value=8),
    Choice(name="d10", value=10),
    Choice(name="d12", value=12),
    Choice(name="d20", value=20),
    Choice(name="d100", value=100),
]


class DnDCog(commands.Cog):
    def __init__(self) -> None:
        pass

    async def _roll(
        self, interaction: discord.Interaction, sides: int, rolls: int = 1
    ) -> None:
        all_rolls = []
        for _ in range(rolls):
            all_rolls.append(random.randint(1, sides))
        rolls_str = f"Rolls: {str(all_rolls)}"
        total_str = f"{'Total' if rolls != 1 else 'Rolled'}: {sum(all_rolls)}"
        if len(rolls_str + total_str) < 2000 and rolls != 1:
            await interaction.response.send_message(f"{rolls_str}\n{total_str}")
            return
        await interaction.response.send_message(total_str)

    @app_commands.command(name="d4", description="Rolls some D4.")
    async def _d4(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 4, rolls)

    @app_commands.command(name="d6", description="Rolls some D6.")
    async def _d6(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 6, rolls)

    @app_commands.command(name="d8", description="Rolls some D8.")
    async def _d8(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 8, rolls)

    @app_commands.command(name="d10", description="Rolls some D10.")
    async def _d10(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 10, rolls)

    @app_commands.command(name="d12", description="Rolls some D12.")
    async def _d12(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 12, rolls)

    @app_commands.command(name="d20", description="Rolls some D20.")
    async def _d20(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 20, rolls)

    @app_commands.command(name="d100", description="Rolls some D100.")
    async def _d100(self, interaction: discord.Interaction, rolls: int = 1) -> None:
        await self._roll(interaction, 100, rolls)

    @app_commands.command(name="rolladv", description="Rolls with advantage.")
    @app_commands.choices(sides=DICE_CHOICES)
    async def _rolladv(self, interaction: discord.Interaction, sides: int) -> None:
        roll1, roll2 = random.randint(1, sides), random.randint(1, sides)
        roll = roll1 if roll1 > roll2 else roll2
        await interaction.response.send_message(f"Rolled with Advantage: {roll}")

    @app_commands.command(name="rolldis", description="Rolls with advantage.")
    @app_commands.choices(sides=DICE_CHOICES)
    async def _rolldis(self, interaction: discord.Interaction, sides: int) -> None:
        """Rolls with disadvantage."""
        roll1, roll2 = random.randint(1, sides), random.randint(1, sides)
        roll = roll1 if roll1 < roll2 else roll2
        await interaction.response.send_message(f"Rolled with Disadvantage: {roll}")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await on_error(ctx, error, None)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        DnDCog(**CONFIGS.cogs.dnd.kwargs), guilds=[discord.Object(id=CONFIGS.guild_id)]
    )
