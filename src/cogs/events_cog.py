import random
from discord.ext import commands
import discord
from configs import CONFIGS


class EventsCog(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as: {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        if CONFIGS.cogs["role_on_join"].enabled:
            role = discord.utils.get(ctx.guild.roles, name=CONFIGS.cogs["role_on_join"]["role"])
            await ctx.author.add_roles(role)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if (
            CONFIGS.cogs["random_insult_on_command"].enabled
            and random.random() < CONFIGS.cogs["random_insult_on_command"]["insult_chance"]
        ):
            insult = f"You're a "
            if random.random() < CONFIGS.cogs["random_insult_on_command"]["adjective_chance"]:
                insult += (
                    random.choice(CONFIGS.cogs["random_insult_on_command"]["adjectives"]) + ", "
                )
            insult += random.choice(CONFIGS.cogs["random_insult_on_command"]["insults"])
            await ctx.send(
                insult, delete_after=CONFIGS.cogs["random_insult_on_command"]["delete_after"]
            )

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f"An error occurred: {str(error)}")
