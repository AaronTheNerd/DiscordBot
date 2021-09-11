from discord.ext import commands
import discord
from config import COG_CONFIGS

class EventsCog(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as: {self.bot.user}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name=COG_CONFIGS["events"]["default_role"])
        await member.add_roles(role)
