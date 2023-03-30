"""A module for the event-based cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
import random
from dataclasses import dataclass, field
from typing import Any

import discord
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, BindingConfig
from utils.error import on_error


@dataclass
class RoleOnJoin:
    enabled: bool
    role_id: int


@dataclass
class RandomInsult:
    enabled: bool
    delete_after: int
    insult_chance: float
    adjective_chance: float
    adjectives: list[str]
    insults: list[str]


@dataclass
class EventsCog(BoundCog):
    bot: commands.Bot
    binding: BindingConfig
    role_on_join: dict[str, Any]
    random_insult_on_command: dict[str, Any]
    parsed_role: RoleOnJoin = field(init=False)
    parsed_insult: RandomInsult = field(init=False)

    def __post_init__(self) -> None:
        super().__init__(self.bot, self.binding)
        self.parsed_role = RoleOnJoin(**self.role_on_join)
        self.parsed_insult = RandomInsult(**self.random_insult_on_command)

    @commands.Cog.listener()
    async def on_member_join(
        self, ctx: commands.Context, member: discord.Member
    ) -> None:
        if not ctx.guild:
            return
        if not self.parsed_role.enabled:
            return
        role = ctx.guild.get_role(self.parsed_role.role_id)
        if role is None:
            return
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        if (
            self.parsed_insult.enabled
            and random.random() < self.parsed_insult.insult_chance
        ):
            insult = f"You're a "
            if random.random() < self.parsed_insult.adjective_chance:
                insult += random.choice(self.parsed_insult.adjectives) + ", "
            insult += random.choice(self.parsed_insult.insults)
            await ctx.send(insult, delete_after=self.parsed_insult.delete_after)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await on_error(ctx, error, self.bot)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        EventsCog(bot, CONFIGS.cogs.events.binding, **CONFIGS.cogs.events.kwargs),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
