from discord.ext import commands
from traceback import TracebackException
from typing import Optional
from configs import CONFIGS

async def on_error(
    ctx: commands.Context, err: commands.CommandError, bot: Optional[commands.Bot]
) -> None:
    await ctx.send(f"**[ERROR]** {err}")
    if bot is None:
        return
    user = bot.get_user(CONFIGS.dev_id)
    if user is None:
        return
    channel = await user.create_dm()
    await channel.send(
        f"An error occurred: {''.join(TracebackException.from_exception(err).format())}"
    )
    return
