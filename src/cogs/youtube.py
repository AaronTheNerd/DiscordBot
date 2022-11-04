# -*- coding: utf-8 -*-

"""
================================================================================
Copyright (c) 2019 Valentin B.
https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d

A simple music bot written in discord.py using youtube-dl.

Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.

Requirements:

Python 3.5+
pip install -U discord.py pynacl youtube-dl

You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
================================================================================
Modified by Aaron Barge 2021

Requirements:

Python installation with access to pip, then simply run
`make setup-venv`
to install pipenv and all the requirements for the project

Additions from Original:
- Added a loopqueue command
- Fixed Resume and Pause functionality
- Modified the nowplaying embed to show whether the current song will loop or 
  if the queue will loop
- Added the ability to queue up playlists
- Made vote skip a variable amount (Broken because of the API)
- Added a force skip for administators
- Removed volume command
================================================================================
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import itertools
import math
import random
from dataclasses import dataclass
from traceback import TracebackException
from typing import Any, Awaitable, Dict, List, Optional

import discord
import youtube_dl
from discord.ext import commands

from utils.search import Search

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ""


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        "username": "discordchatbot69@gmail.com",
        "password": "~<G>$)9H4yUS<8:}",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(
        self,
        ctx: commands.Context,
        source: discord.FFmpegPCMAudio,
        *,
        data: dict,
        volume: float = 0.5,
    ) -> None:
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration = int(data.get("duration"))
        self.duration_str = self.parse_duration(int(data.get("duration")))
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.stream_url = data.get("url")

    def __str__(self) -> str:
        return f"**{self.title}** by **{self.uploader}**"

    @classmethod
    async def create_source(
        cls,
        ctx: commands.Context,
        _search: Search,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> List[Awaitable[YTDLSource]]:
        async def func(search: str, loop: asyncio.AbstractEventLoop, is_url: bool) -> YTDLSource:
            if not is_url:
                partial = functools.partial(
                    cls.ytdl.extract_info, search, download=False, process=False
                )
                data = await loop.run_in_executor(None, partial)
                if data is None:
                    raise YTDLError(f"Couldn't find anything that matches `{search}`")
                if "entries" not in data:
                    process_info = data
                else:
                    process_info = None
                    for entry in data["entries"]:
                        if entry:
                            process_info = entry
                            break
                    if process_info is None:
                        raise YTDLError(f"Couldn't find anything that matches `{search}`")
                webpage_url = process_info["webpage_url"]
                print(webpage_url)
            else:
                webpage_url = search
            partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
            processed_info = await loop.run_in_executor(None, partial)
            if processed_info is None:
                raise YTDLError(f"Couldn't fetch `{webpage_url}`")
            if "entries" not in processed_info:
                info = processed_info
            else:
                info = None
                while info is None:
                    try:
                        info = processed_info["entries"].pop(0)
                    except IndexError:
                        raise YTDLError(f"Couldn't retrieve any matches for `{webpage_url}`")
            return cls(ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)

        loop = loop or asyncio.get_event_loop()
        return [func(search, loop, _search.is_url) for search in _search.searches]

    @classmethod
    async def create_source_playlist(
        cls,
        ctx: commands.Context,
        _search: Search,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> List[Awaitable[YTDLSource]]:
        search = _search.searches[0]
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f"Couldn't find anything that matches `{search}`")
        if "entries" not in data:
            entries = [data]
        else:
            entries = []
            for entry in data["entries"]:
                if entry:
                    entries.append(entry)
            if len(entries) == 0:
                raise YTDLError(f"Couldn't find anything that matches `{search}`")

        coroutines = []
        for entry in entries:
            try:
                coroutines += await cls.create_source(ctx, Search(f"https://www.youtube.com/watch?v={entry['url']}"), loop=loop)
            except:
                pass
        return coroutines

    @staticmethod
    def parse_duration(duration: int) -> str:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration_list = []
        if days > 0:
            duration_list.append(f"{days} days")
        if hours > 0:
            duration_list.append(f"{hours} hours")
        if minutes > 0:
            duration_list.append(f"{minutes} minutes")
        if seconds > 0:
            duration_list.append(f"{seconds} seconds")
        return ", ".join(duration_list)


class Song:
    __slots__ = ("source", "requester", "pending")

    def __init__(self, source: YTDLSource, pending: bool = False) -> None:
        self.source = source
        self.requester = source.requester
        self.pending = pending

    @classmethod
    def create_pending(cls, source: Awaitable[YTDLSource]) -> Awaitable[Song]:
        async def func(source: Awaitable[YTDLSource]) -> Song:
            return cls(await source)
        return func(source)


    def create_embed(self, loop: bool = False, loopqueue: bool = False) -> discord.Embed:
        embed = (
            discord.Embed(
                title="Now playing",
                description=f"```css\n{self.source.title}\n```",
                color=discord.Color.blurple(),
            )
            .add_field(name="Duration", value=self.source.duration_str)
            .add_field(name="Requested by", value=self.requester.mention)
            .add_field(
                name="Uploader", value=f"[{self.source.uploader}]({self.source.uploader_url})"
            )
            .add_field(name="URL", value=f"[Click]({self.source.url})")
            .add_field(name="Loop", value=f'{"✅" if loop else "❌"}')
            .add_field(name="Loop Queue", value=f'{"✅" if loopqueue else "❌"}')
            .set_thumbnail(url=self.source.thumbnail)
        )
        return embed


class SongQueue(asyncio.Queue):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.song_added_flag = asyncio.Event()
        self.lock = asyncio.Lock()

    def __getitem__(self, item) -> Any | List[Any]:
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self) -> int:
        return self.qsize()

    async def put(self, *args, **kwargs) -> None:
        async with self.lock:
            await super().put(*args, **kwargs)
            self.song_added_flag.set()

    async def get(self, *args, **kwargs) -> Any:
        async with self.lock:
            result = await super().get(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
        return result

    def clear(self) -> None:
        self._queue.clear()

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def remove(self, index: int) -> None:
        del self._queue[index]

    async def lazy_load_task(self) -> None:
        while True:
            await self.song_added_flag.wait()
            async with self.lock:
                for index, song in enumerate(self._queue_):
                    if inspect.isawaitable(song):
                        try:
                            self._queue[index] = await song
                        except Exception:
                            del self._queue[index]
                        break
                else:
                    self.song_added_flag.clear()



class VoiceState:
    def __init__(self, bot: commands.Bot, cog: Music, ctx: commands.Context) -> None:
        self.bot = bot
        self.cog = cog
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._loopqueue = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())
        self.lazy_loader = bot.loop.create_task(self.songs.lazy_load_task())

    def __del__(self) -> None:
        self.audio_player.cancel()
        self.lazy_loader.cancel()

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def loopqueue(self) -> bool:
        return self._loopqueue

    @loopqueue.setter
    def loopqueue(self, value: bool) -> None:
        self._loopqueue = value

    @property
    def is_playing(self) -> bool:
        return self.voice is not None and self.current is not None

    async def get_new_current(self) -> None:
        self.current = await self.songs.get()

    async def audio_player_task(self) -> None:
        while True:
            self.next.clear()
            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                if self.loopqueue and self.current is not None:
                    await self.songs.put(self.current)
                self.current = None
                try:
                    await asyncio.wait_for(self.get_new_current(), 180)
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.disconnect())
                    return
            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.now_playing_embed())
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name=self.current.source.title
                )
            )
            await self.next.wait()

    def play_next_song(self, error: Optional[Exception] = None) -> None:
        if error:
            pass
            #raise VoiceError(str(error))
        self.next.set()

    def skip(self) -> None:
        self.skip_votes.clear()
        if self.is_playing:
            self.voice.stop()

    async def stop(self) -> None:
        self.songs.clear()
        if self.voice is not None:
            await self.voice.disconnect()
            self.voice = None

    async def disconnect(self) -> None:
        await self._ctx.invoke(self.cog._leave)

    def now_playing_embed(self) -> discord.Embed:
        return self.current.create_embed(self._loop, self._loopqueue)


@dataclass
class VoteSkipConfigs:
    exclude_idle: bool
    requester_autoskip: bool
    fraction: float


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot, voteskip: Dict[str, Any]) -> None:
        self.bot = bot
        self.voice_states = {}
        self.voteskip = VoteSkipConfigs(**voteskip)

    def get_voice_state(self, ctx: commands.Context) -> VoiceState:
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, self, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self) -> None:
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage("This command can't be used in DM channels.")
        return True

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await ctx.send(
            f"An error occurred: {''.join(TracebackException.from_exception(error).format())}"
        )

    @commands.command(name="join", aliases=["summon"], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context) -> None:
        """Joins a voice channel."""
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="disconnect", aliases=["dc", "leave", "dis"])
    async def _leave(self, ctx: commands.Context, silent: bool = False) -> None:
        """Clears the queue and leaves the voice channel."""
        if not ctx.voice_state.voice:
            if not silent:
                await ctx.send("Not connected to any voice channel.")
            return
        await ctx.voice_state.stop()
        await self.bot.change_presence(status=discord.Status.idle)
        del self.voice_states[ctx.guild.id]

    @commands.command(name="nowplaying", aliases=["np"])
    async def _now(self, ctx: commands.Context) -> None:
        """Displays the currently playing song."""
        if ctx.voice_state.current is not None:
            await ctx.send(embed=ctx.voice_state.now_playing_embed())
        else:
            await ctx.send("Nothing playing at the moment.")

    @commands.command(name="pause", aliases=["stop"])
    async def _pause(self, ctx: commands.Context) -> None:
        """Pauses the currently playing song."""
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="resume", aliases=["re", "res", "continue"])
    async def _resume(self, ctx: commands.Context) -> None:
        """Resumes a currently paused song."""
        if ctx.voice_state.is_playing is not None and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="clear", aliases=["cl"])
    async def _stop(self, ctx: commands.Context) -> None:
        """Stops playing song and clears the queue."""
        ctx.voice_state.songs.clear()
        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction("⏹")

    @commands.command(name="skip", aliases=["next", "s"])
    @commands.has_permissions(administrator=True)
    async def _skip(self, ctx: commands.Context) -> None:
        """Skips a song without vote."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")
        await ctx.message.add_reaction("⏭")
        ctx.voice_state.skip()

    @commands.command(name="voteskip", aliases=["vs"])
    async def _voteskip(self, ctx: commands.Context) -> None:
        """Vote to skip a song.

        The requestor can skip the current song without a vote.
        """
        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")
        voter = ctx.message.author
        if self.voteskip.requester_autoskip and voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction("⏭")
            ctx.voice_state.skip()
        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)
            if ctx.author.voice is None:
                ctx.send("You're not in a vc.")
            members = ctx.author.voice.channel.members
            # members = ctx.voice_state.voice.channel.members
            print(f"MEMBERS {members}")
            if self.voteskip.exclude_idle:
                members = [member for member in members if member.status != "idle"]
            votes_needed = self.voteskip.fraction * float(len(members) - 1)
            await ctx.send(f"Whose in vc: {str([member.name for member in members])}")
            await ctx.send(
                f"Skip vote added, currently at **{total_votes}/{str(math.ceil(votes_needed))}**"
            )
            if total_votes >= votes_needed:
                await ctx.message.add_reaction("⏭")
                ctx.voice_state.skip()
        else:
            await ctx.send("You have already voted to skip this song.")

    @commands.command(name="queue", aliases=["q"])
    async def _queue(self, ctx: commands.Context, *, page: int = 1) -> None:
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")
        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            if not inspect.isawaitable(song):
                queue += f"`{i + 1}.` [**{song.source.title}**]({song.source.url})\n"
            else:
                queue += f"`{i + 1}.` Pending...\n"
        embed = discord.Embed(
            description=f"**{len(ctx.voice_state.songs)} tracks:**\n\n{queue}"
        ).set_footer(text=f"Viewing page {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(name="shuffle", aliases=["random"])
    async def _shuffle(self, ctx: commands.Context) -> None:
        """Shuffles the queue."""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")
        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction("✅")

    @commands.command(name="remove", aliases=["rm"])
    async def _remove(self, ctx: commands.Context, index: int) -> None:
        """Removes a song from the queue at a given index."""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")
        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction("✅")

    @commands.command(name="loop")
    async def _loop(self, ctx: commands.Context) -> None:
        """Toggle whether to loop the currently playing song."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")
        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction("✅")

    @commands.command(name="loopqueue", aliases=["lq"])
    async def _loopqueue(self, ctx: commands.Context) -> None:
        """Toggle whether to loop the queue."""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")
        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loopqueue = not ctx.voice_state.loopqueue
        await ctx.message.add_reaction("✅")

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx: commands.Context, *, search: str) -> None:
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        async with ctx.typing():
            try:
                _search = Search(search)
                if _search.playlist:
                    futures = await YTDLSource.create_source_playlist(
                        ctx, _search, loop=self.bot.loop
                    )
                else:
                    futures = await YTDLSource.create_source(ctx, _search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send(f"An error occurred while processing this request: {str(e)}")
            else:
                for future in futures:
                    song = Song.create_pending(future)
                    await ctx.voice_state.songs.put(song)
                await ctx.invoke(self._queue)

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context) -> None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You are not connected to any voice channel.")
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("Bot is already in a voice channel.")
