"""A module for the event-based cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
import random
from dataclasses import dataclass

import discord
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, EventsConfig


@dataclass
class EventsCog(BoundCog):
    bot: commands.Bot
    configs: EventsConfig

    def __post_init__(self) -> None:
        super().__init__(self.bot, self.configs.binding)

    @commands.Cog.listener()
    async def on_member_join(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        if not ctx.guild:
            return
        if not self.configs.role_on_join.enabled:
            return
        role = ctx.guild.get_role(self.configs.role_on_join.role_id)
        if role is None:
            return
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        if (
            self.configs.random_insult_on_command.enabled
            and random.random() < self.configs.random_insult_on_command.insult_chance
        ):
            insult = f"You're a "
            if random.random() < self.configs.random_insult_on_command.adjective_chance:
                insult += (
                    random.choice(self.configs.random_insult_on_command.adjectives)
                    + ", "
                )
            insult += random.choice(self.configs.random_insult_on_command.insults)
            await ctx.send(
                insult, delete_after=self.configs.random_insult_on_command.delete_after
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        EventsCog(bot, CONFIGS.cogs.events),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
