from discord.ext import commands

from configs import BindingConfig
from utils.error import on_error


class BoundCog(commands.Cog):
    def __init__(self, bot: commands.Bot, binding: BindingConfig):
        self.bot = bot
        self.binding = binding

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        if self.binding.enabled and ctx.channel.id != self.binding.channel_id:
            raise commands.CommandError("The Music cog is not bound to this channel")
        
    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await on_error(ctx, error, self.bot)
