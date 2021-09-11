from discord.ext import commands

class SpotifyCog(commands.Cog, name="Spotify"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='join', aliases=['summon'])
    async def join(ctx):
        pass

    @commands.command(name='play', aliases=['p'])
    async def play(ctx):
        pass

    @commands.command(name='playtop', aliases=['pt', 'ptop'])
    async def play_top(ctx):
        pass    

    @commands.command(name='playskip', aliases=['ps', 'pskip', 'playnow', 'pn'])
    async def play_skip(ctx):
        pass

    @commands.command(name='search', aliases=['find'])
    async def search(ctx):
        pass

    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing(ctx):
        pass

    @commands.command(name='seek')
    async def seek(ctx):
        pass

    @commands.command(name='rewind', aliases=['rwd'])
    async def rewind(ctx):
        pass

    @commands.command(name='forward', aliases=['fwd'])
    async def forward(ctx):
        pass

    @commands.command(name='replay')
    async def replay(ctx):
        pass

    @commands.command(name='skip', aliases=['next', 's'])
    async def skip(ctx):
        pass

    @commands.command(name='pause', aliases=['stop'])
    async def pause(ctx):
        pass

    @commands.command(name='resume', aliases=['re', 'res', 'continue'])
    async def resume(ctx):
        pass

    @commands.command(name='lyrics', aliases=['l', 'ly'])
    async def lyrics(ctx):
        pass

    @commands.command(name='disconnect', aliases=['dc', 'leave', 'dis'])
    async def disconnect(ctx):
        pass
