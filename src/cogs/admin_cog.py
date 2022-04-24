from discord.ext import commands


class AdminCog(commands.Cog, name="AdminsOnly"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command("shutdown")
    @commands.has_permissions(administrator=True)
    async def _shutdown(self, ctx: commands.Context):
        for vc in self.bot.voice_clients:
            await vc.disconnect()
        await self.bot.close()

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f"An error occurred: {str(error)}")
