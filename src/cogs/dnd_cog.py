import random

from discord.ext import commands

class DnDCog(commands.Cog, name="DnD"):
    def __init__(self):
        pass

    @commands.command(name='roll')
    async def _roll(self, ctx, num_of_sides: int, num_of_rolls: int = 1):
        """Rolls a dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, num_of_sides))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d4')
    async def _d4(self, ctx, num_of_rolls: int = 1):
        """Rolls a 4-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 4))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d6')
    async def _d6(self, ctx, *, num_of_rolls: int = 1):
        """Rolls a 6-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 6))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d8')
    async def _d8(self, ctx, *, num_of_rolls: int = 1):
        """Rolls an 8-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 8))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d10')
    async def _d10(self, ctx, *, num_of_rolls: int = 1):
        """Rolls a 10-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 10))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d12')
    async def _d12(self, ctx, *, num_of_rolls: int = 1):
        """Rolls a 12-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 12))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d20')
    async def _d20(self, ctx, *, num_of_rolls: int = 1):
        """Rolls a 20-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 20))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name='d100')
    async def _d100(self, ctx, *, num_of_rolls: int = 1):
        """Rolls a 100-sided dice."""
        rolls = []
        for i in range(num_of_rolls):
            rolls.append(random.randint(1, 100))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')
