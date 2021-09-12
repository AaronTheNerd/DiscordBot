import randfacts
from discord.ext import commands

class MiscCog(commands.Cog, name="Miscellaneous"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello', aliases=['hey', 'howdy'])
    async def _hello(self, ctx):
        await ctx.send(f'Hello, {ctx.author}!')

    @commands.command(name='fact', aliases=['randfact', 'rf'])
    async def _fact(self, ctx):
        await ctx.send(f"Did you know?\n{randfacts.get_fact()}")
