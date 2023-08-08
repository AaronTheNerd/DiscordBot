"""A module for the help command

Written by Aaron Barge
Copyright 2022
"""
from typing import Any, Optional
from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, HelpConfig


class CogSelect(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]) -> None:
        super().__init__(
            placeholder="Choose a cog to view",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message()


@dataclass
class HelpView(discord.ui.View):
    options: list[discord.SelectOption]

    def __post_init__(self):
        super().__init__()
        self.add_item(CogSelect(self.options))


@dataclass
class HelpCog(BoundCog):
    bot: commands.Bot
    configs: HelpConfig

    def __post_init__(self) -> None:
        super().__init__(self.bot, self.configs.binding)

    def build_full_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Help",
            description="List of all commands",
            color=discord.Color.blurple(),
        )
        for command in self.bot.tree.walk_commands():
            embed.add_field(name=command.name, value=command.description)
        return embed

    @app_commands.command(name="help", description="Help message.")
    async def _help(
        self, interaction: discord.Interaction, input: Optional[str]
    ) -> None:
        options = [
            discord.SelectOption(label=cog_name, description=cog.description)
            for cog_name, cog in self.bot.cogs.items()
        ]
        options = [
            option for option in options if option != "HelpCog" and option != "EventCog"
        ]
        if input is None:
            await interaction.response.send_message(
                embed=self.build_full_embed(), view=HelpView(options), ephemeral=True
            )
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        HelpCog(bot, CONFIGS.cogs.help),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
