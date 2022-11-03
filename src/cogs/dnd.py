import random

from discord.ext import commands


class DnDCog(commands.Cog, name="DnD"):
    def __init__(self) -> None:
        pass

    @commands.command(name="roll")
    async def _roll(self, ctx: commands.Context, num_of_sides: int, num_of_rolls: int = 1) -> None:
        """Rolls a dice."""
        rolls = []
        for _ in range(num_of_rolls):
            rolls.append(random.randint(1, num_of_sides))
        rolls_str = f"Rolls: {str(rolls)}"
        if len(rolls_str) < 2000 and num_of_rolls != 1:
            await ctx.send(rolls_str)
        await ctx.send(f"{'Total' if num_of_rolls != 1 else 'Rolled'}: {sum(rolls)}")

    @commands.command(name="d4")
    async def _d4(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 4-sided dice."""
        await ctx.invoke(self._roll, 4, num_of_rolls)

    @commands.command(name="d6")
    async def _d6(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 6-sided dice."""
        await ctx.invoke(self._roll, 6, num_of_rolls)

    @commands.command(name="d8")
    async def _d8(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls an 8-sided dice."""
        await ctx.invoke(self._roll, 8, num_of_rolls)

    @commands.command(name="d10")
    async def _d10(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 10-sided dice."""
        await ctx.invoke(self._roll, 10, num_of_rolls)

    @commands.command(name="d12")
    async def _d12(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 12-sided dice."""
        await ctx.invoke(self._roll, 12, num_of_rolls)

    @commands.command(name="d20")
    async def _d20(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 20-sided dice."""
        await ctx.invoke(self._roll, 20, num_of_rolls)

    @commands.command(name="d100")
    async def _d100(self, ctx: commands.Context, num_of_rolls: int = 1) -> None:
        """Rolls a 100-sided dice."""
        await ctx.invoke(self._roll, 100, num_of_rolls)

    @commands.command(name="rolladv", aliases=["rolla", "rolladvantage", "ra"])
    async def _rolladv(self, ctx: commands.Context, num_of_sides: int) -> None:
        """Rolls with advantage."""
        roll1, roll2 = random.randint(1, num_of_sides), random.randint(1, num_of_sides)
        roll = roll1 if roll1 > roll2 else roll2
        await ctx.send(f"Rolled with Advantage: {roll}")

    @commands.command(name="rolldis", aliases=["rolld", "rolldisadvantage", "rd"])
    async def _rolldis(self, ctx: commands.Context, num_of_sides: int) -> None:
        """Rolls with disadvantage."""
        roll1, roll2 = random.randint(1, num_of_sides), random.randint(1, num_of_sides)
        roll = roll1 if roll1 < roll2 else roll2
        await ctx.send(f"Rolled with Disadvantage: {roll}")

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await ctx.send(f"An error occurred: {str(error)}")
