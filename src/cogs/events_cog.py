import random
from discord.ext import commands
import discord
from config import ROLE_ON_JOIN_CONFIGS, RANDOM_INSULT_CONFIGS

class EventsCog(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as: {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        if ROLE_ON_JOIN_CONFIGS["enabled"]:
            role = discord.utils.get(ctx.guild.roles, name=ROLE_ON_JOIN_CONFIGS["role"])
            await ctx.add_roles(role)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if RANDOM_INSULT_CONFIGS['enabled'] and random.random() < RANDOM_INSULT_CONFIGS["insult_chance"]:
            insult = f'You\'re a {(random.choice(RANDOM_INSULT_CONFIGS["adjectives"]) + ", ") if random.random() < RANDOM_INSULT_CONFIGS["adjective_chance"] else ""}{random.choice(RANDOM_INSULT_CONFIGS["insults"])}'
            await ctx.send(insult, delete_after=RANDOM_INSULT_CONFIGS["delete_after"])
