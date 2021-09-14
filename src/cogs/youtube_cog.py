import asyncio

import discord
from discord.ext import commands

class YoutubeCog(commands.Cog, name="Youtube"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='join', aliases=['summon'])
    async def _join(self, ctx):
        if ctx.author.voice: # If the author is a voice channel
            channel = ctx.author.voice.channel # Get voice channel of author
            if ctx.voice_client: # If I am in a voice channel
                await ctx.voice_client.disconnect() # Leave the old voice channel
            await channel.connect() # Go to new voice channel
        else:
            await ctx.send(f"{ctx.author}, you need to be in a voice channel to use this command!")

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx, url):
        pass

    @commands.command(name='playtop', aliases=['pt', 'ptop'])
    async def _play_top(self, ctx):
        pass    

    @commands.command(name='playskip', aliases=['ps', 'pskip', 'playnow', 'pn'])
    async def _play_skip(self, ctx):
        pass

    @commands.command(name='search', aliases=['find'])
    async def _search(self, ctx):
        pass

    @commands.command(name='nowplaying', aliases=['np'])
    async def _now_playing(self, ctx):
        pass

    @commands.command(name='seek')
    async def _seek(self, ctx):
        pass

    @commands.command(name='rewind', aliases=['rwd'])
    async def _rewind(self, ctx):
        pass

    @commands.command(name='forward', aliases=['fwd'])
    async def _forward(self, ctx):
        pass

    @commands.command(name='replay')
    async def _replay(self, ctx):
        pass

    @commands.command(name='skip', aliases=['next', 's'])
    async def _skip(self, ctx):
        pass

    @commands.command(name='pause', aliases=['stop'])
    async def _pause(self, ctx):
        pass

    @commands.command(name='resume', aliases=['re', 'res', 'continue'])
    async def _resume(self, ctx):
        pass

    @commands.command(name='lyrics', aliases=['l', 'ly'])
    async def _lyrics(self, ctx):
        pass

    @commands.command(name='disconnect', aliases=['dc', 'leave', 'dis'])
    async def _disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send(f"{ctx.author}, I am not in a voice channel!")

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx):
        pass

    @commands.command(name='loopqueue', aliases=['qloop', 'lq', 'queueloop'])
    async def _loop_queue(self, ctx):
        pass

    @commands.command(name='move', aliases=['m', 'mv'])
    async def _move(self, ctx):
        pass

    @commands.command(name='skipto', aliases=['st'])
    async def _skip_to(self, ctx):
        pass

    @commands.command(name='shuffle', aliases=['random'])
    async def _shuffle(self, ctx):
        pass

    @commands.command(name='remove', aliases=['rm'])
    async def _remove(self, ctx):
        pass

    @commands.command(name='clear', aliases=['cl'])
    async def _clear(self, ctx):
        pass

    @commands.command(name='leavecleanup', aliases=['lc'])
    async def _leave_cleanup(self, ctx):
        pass

    @commands.command(name='removedupes', aliases=['rmd', 'rd', 'drm'])
    async def _remove_dupes(self, ctx):
        pass
