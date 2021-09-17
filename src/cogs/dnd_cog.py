import random

from discord.ext import commands

class DnDCog(commands.Cog, name="DnD"):
    def __init__(self):
        pass

    @commands.command(name='roll')
    async def _roll(self, ctx, *, num_of_sides: int):
        """Rolls a dice."""
        await ctx.send(f"Rolled: {random.randint(1, num_of_sides)}")

    @commands.command(name='d4')
    async def _d4(self, ctx):
        """Rolls a 4-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 4)}")

    @commands.command(name='d6')
    async def _d6(self, ctx):
        """Rolls a 6-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 6)}")

    @commands.command(name='d8')
    async def _d8(self, ctx):
        """Rolls an 8-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 8)}")

    @commands.command(name='d10')
    async def _d10(self, ctx):
        """Rolls a 10-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 10)}")

    @commands.command(name='d12')
    async def _d12(self, ctx):
        """Rolls a 12-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 12)}")

    @commands.command(name='d20')
    async def _d20(self, ctx):
        """Rolls a 20-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 20)}")

    @commands.command(name='d100')
    async def _d100(self, ctx):
        """Rolls a 100-sided dice."""
        await ctx.send(f"Rolled: {random.randint(1, 100)}")

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')
