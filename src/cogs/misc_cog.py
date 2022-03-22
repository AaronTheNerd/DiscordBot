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
        """Gives a random fact."""
        await ctx.send(f"Did you know?\n{randfacts.get_fact()}")

    @commands.command(name='ping')
    async def _ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}")

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')
