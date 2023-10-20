"""A module for the miscellaneous cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
from dataclasses import dataclass
import random

import discord
import randfacts
from discord import app_commands
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, MiscConfig

import pokebase as pb


@dataclass
class MiscCog(BoundCog):
    bot: commands.Bot
    configs: MiscConfig

    def __post_init__(self) -> None:
        super().__init__(self.bot, self.configs.binding)

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

    @app_commands.command(name="pokemon", description="Generates a random pokemon")
    async def _pokemon(self, interaction: discord.Interaction) -> None:
        max_id = 1017
        await interaction.response.send_message("Searching...")
        pokemons = []
        for _ in range(3):
            pokemon_id = random.randint(1, max_id)
            pokemon = pb.pokemon(pokemon_id)
            pokemons.append(pokemon)
        content = f"""Searching... COMPLETE

Here are your options:
"""
        embeds = [
            discord.Embed(
                title=f"#{pokemon.id}: {pokemon.name}", color=discord.Color.blurple()
            ).set_image(url=pokemon.sprites.front_default)
            for pokemon in pokemons
        ]
        await interaction.edit_original_response(content=content, embeds=embeds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        MiscCog(bot, CONFIGS.cogs.misc),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
