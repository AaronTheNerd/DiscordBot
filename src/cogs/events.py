"""A module for the event-based cog of the bot.

Written by Aaron Barge
Copyright 2022
"""
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List

import discord
from discord.ext import commands


@dataclass
class RoleOnJoin:
    enabled: bool
    role: str = field(default="")


@dataclass
class RandomInsult:
    enabled: bool
    delete_after: int
    insult_chance: float
    adjective_chance: float
    adjectives: List[str]
    insults: List[str]


class EventsCog(commands.Cog, name="Events"):
    def __init__(
        self, bot, role_on_join: Dict[str, Any], random_insult_on_command: Dict[str, Any]
    ) -> None:
        self.bot = bot
        self.role = RoleOnJoin(**role_on_join)
        self.insult = RandomInsult(**random_insult_on_command)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"Logged in as: {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_join(self, ctx: commands.Context, member: discord.Member) -> None:
        if self.role.enabled:
            role = discord.utils.get(ctx.guild.roles, name=self.role.role)  # type: ignore
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        if self.insult.enabled and random.random() < self.insult.insult_chance:
            insult = f"You're a "
            if random.random() < self.insult.adjective_chance:
                insult += random.choice(self.insult.adjectives) + ", "
            insult += random.choice(self.insult.insults)
            await ctx.send(insult, delete_after=self.insult.delete_after)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await ctx.send(f"An error occurred: {str(error)}")
