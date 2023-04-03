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
Modified by Aaron Barge 2021-2022

Requirements:

Python 3.8 installation with access to pip, then simply run
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
- Added ability to use spotify playlists/songs
- Added ability to lazy load songs to reduce server strain on long playlists
- Made the queue command delete after some set time
- Made the automated now playing embed delete after the song ends
================================================================================
"""

from __future__ import annotations

import asyncio
import functools
import itertools
import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Optional

import discord
import youtube_dl
from discord.ext import commands

from cog import BoundCog
from configs import CONFIGS, YoutubeConfig
from utils.error import on_error
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
        requester: discord.User | discord.Member,
        channel: discord.abc.MessageableChannel,
        search: str,
        source: discord.FFmpegPCMAudio,
        *,
        data: dict[str, Any],
        volume: float = 0.5,
    ) -> None:
        super().__init__(source, volume)

        self.requester = requester
        self.channel = channel
        self.search = search
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        if date is not None:
            self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        duration = data.get("duration")
        if duration is not None:
            self.duration = int(duration)
            self.duration_str = self.parse_duration(duration)
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
        requester: discord.User | discord.Member,
        channel: discord.abc.MessageableChannel,
        _search: Search,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> list[FutureYTDLSource]:
        async def func(
            search: str, loop: Optional[asyncio.AbstractEventLoop], is_url: bool
        ) -> YTDLSource:
            loop = loop or asyncio.get_event_loop()
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
                        raise YTDLError(
                            f"Couldn't find anything that matches `{search}`"
                        )
                webpage_url = process_info["webpage_url"]
            else:
                webpage_url = search
            partial = functools.partial(
                cls.ytdl.extract_info, webpage_url, download=False
            )
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
                        raise YTDLError(
                            f"Couldn't retrieve any matches for `{webpage_url}`"
                        )
            return cls(
                requester,
                channel,
                search,
                discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS),
                data=info,
            )

        return [
            FutureYTDLSource(search, func(search, loop, _search.is_url))
            for search in _search.searches
        ]

    @classmethod
    async def create_source_playlist(
        cls,
        requester: discord.User | discord.Member,
        channel: discord.abc.MessageableChannel,
        _search: Search,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> list[FutureYTDLSource]:
        search = _search.searches[0]
        loop = loop or asyncio.get_event_loop()
        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False
        )
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
                coroutines += await cls.create_source(
                    requester,
                    channel,
                    Search(f"https://www.youtube.com/watch?v={entry['url']}"),
                    loop=loop,
                )
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


@dataclass
class FutureYTDLSource:
    raw_search: str
    future: Awaitable[YTDLSource]


@dataclass(slots=True)
class Song:
    source: YTDLSource
    requester: discord.Member | discord.User = field(init=False)

    def __post_init__(self) -> None:
        self.requester = self.source.requester

    @classmethod
    def create_pending(cls, source: FutureYTDLSource) -> FutureSong:
        async def func(source: FutureYTDLSource) -> Song:
            return cls(await source.future)

        return FutureSong(source.raw_search, func(source))

    def create_embed(
        self, loop: bool = False, loopqueue: bool = False
    ) -> discord.Embed:
        embed = (
            discord.Embed(
                title="Now playing",
                description=f"```css\n{self.source.title}\n```",
                color=discord.Color.blurple(),
            )
            .add_field(name="Duration", value=self.source.duration_str)
            .add_field(name="Requested by", value=self.requester.mention)
            .add_field(
                name="Uploader",
                value=f"[{self.source.uploader}]({self.source.uploader_url})",
            )
            .add_field(name="URL", value=f"[Click]({self.source.url})")
            .add_field(name="Loop", value=f'{"✅" if loop else "❌"}')
            .add_field(name="Loop Queue", value=f'{"✅" if loopqueue else "❌"}')
            .set_thumbnail(url=self.source.thumbnail)
        )
        return embed

    def __str__(self) -> str:
        return f"[**{self.source.title}**]({self.source.url})"


@dataclass
class FutureSong:
    raw_search: str
    future: Awaitable[Song]

    def __str__(self) -> str:
        return f"'{self.raw_search}'"


@dataclass
class SongQueue(asyncio.Queue):
    lazy_load: int
    max_lazy_load: int

    songs_modified: asyncio.Event = field(default_factory=asyncio.Event)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _queue: deque[Song | FutureSong] = field(init=False)

    def __post_init__(self) -> None:
        super().__init__()

    def __getitem__(self, item) -> Song | FutureSong | list[Song | FutureSong]:
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self) -> int:
        return self.qsize()

    async def put(self, *args, **kwargs) -> None:
        await super().put(*args, **kwargs)
        self.songs_modified.set()

    async def get(self) -> Song:
        async with self.lock:
            result = await super().get()
            if type(result) is FutureSong:
                result = await result.future
        self.songs_modified.set()
        return result  # type: ignore

    def slice(self, start, stop, step=1) -> list[Song | FutureSong]:
        return list(itertools.islice(self._queue, start, stop, step))

    def clear(self) -> None:
        self._queue.clear()

    def shuffle(self) -> None:
        random.shuffle(self._queue)
        self.songs_modified.set()

    def remove(self, index: int) -> None:
        del self._queue[index]
        self.songs_modified.set()

    def move(self, index_from: int, index_to: int) -> None:
        self._queue.insert(index_to, self._queue[index_from])
        if index_to < index_from:
            index_from += 1
        del self._queue[index_from]
        self.songs_modified.set()

    async def lazy_load_task(self) -> None:
        has_awaitable: bool = True
        while True:
            await self.songs_modified.wait()
            has_awaitable = False
            async with self.lock:
                if self.max_lazy_load < len(
                    list(filter(lambda x: type(x) is not FutureSong, self._queue))
                ):
                    self.songs_modified.clear()
                    continue
                for index, song in enumerate(self._queue):
                    if index >= self.lazy_load:
                        break
                    if type(song) is FutureSong:
                        try:
                            self._queue[index] = await song.future
                        except Exception:
                            del self._queue[index]
                            break
                        else:
                            has_awaitable = True
                            break
            if not has_awaitable:
                self.songs_modified.clear()


@dataclass
class VoiceState:
    bot: commands.Bot
    cog: Music
    _ctx: commands.Context

    songs: SongQueue = field(init=False)
    audio_player: asyncio.Task = field(init=False)
    lazy_loader: asyncio.Task = field(init=False)

    current: Optional[Song] = None
    voice: Optional[discord.VoiceClient] = None
    next: asyncio.Event = field(default_factory=asyncio.Event)

    _loop: bool = False
    _loopqueue: bool = False
    _volume: float = 0.5
    skip_votes: set = field(default_factory=set)

    def __post_init__(self) -> None:
        self.songs = SongQueue(
            self.cog.configs.lazy_load, self.cog.configs.max_lazy_load
        )
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self.lazy_loader = self.bot.loop.create_task(self.songs.lazy_load_task())

    def cancel(self) -> None:
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
        msg = None
        while True:
            self.next.clear()
            if not self.loop:
                if self.loopqueue and self.current is not None:
                    remade_current = await self.remake_current()
                    if remade_current is not None:
                        await self.songs.put(remade_current)
                self.current = None
                try:
                    await asyncio.wait_for(
                        self.get_new_current(), self.cog.configs.disconnect_timeout
                    )
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.disconnect())
                    return
            elif self.current is not None:
                remade_current = await self.remake_current()
                if remade_current is not None:
                    self.current = await remade_current.future
            if self.current is not None:
                self.current.source.volume = self._volume
                self.skip_votes.clear()
                if self.voice is not None:
                    self.voice.play(self.current.source, after=self.play_next_song)
                if msg is not None:
                    await msg.delete()
                    msg = None
                embed = self.now_playing_embed()
                if embed is not None:
                    msg = await self.current.source.channel.send(embed=embed)
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening,
                        name=self.current.source.title,
                    )
                )
                await self.next.wait()

    async def remake_current(self) -> FutureSong | None:
        if self.current is None:
            return
        requester = self.current.source.requester
        channel = self.current.source.channel
        url = Search(self.current.source.search)
        return Song.create_pending(
            (await YTDLSource.create_source(requester, channel, url))[0]
        )

    def play_next_song(self, error: Optional[Exception] = None) -> None:
        if error:
            raise VoiceError(str(error))
        self.next.set()

    def skip(self) -> None:
        self.skip_votes.clear()
        if self.is_playing and self.voice is not None:
            self.voice.stop()

    async def stop(self) -> None:
        self.songs.clear()
        if self.voice is None:
            return
        await self.voice.disconnect()
        self.voice = None

    async def disconnect(self) -> None:
        await self._ctx.invoke(self.cog._leave)

    def now_playing_embed(self) -> Optional[discord.Embed]:
        if self.current is not None:
            return self.current.create_embed(self._loop, self._loopqueue)


@dataclass
class Music(BoundCog):
    bot: commands.Bot
    configs: YoutubeConfig
    voice_state: Optional[VoiceState] = None

    def __post_init__(self) -> None:
        super().__init__(self.bot, self.configs.binding)

    def cog_unload(self) -> None:
        if self.voice_state is None:
            return
        self.bot.loop.create_task(self.voice_state.stop())

    def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                "This command can't be used in DM channels."
            )
        return True

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        await super().cog_before_invoke(ctx)
        if self.voice_state is None:
            self.voice_state = VoiceState(self.bot, self, ctx)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        await on_error(ctx, error, self.bot)

    @commands.command(name="join", aliases=["summon"], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context) -> None:
        """Joins a voice channel."""
        if (
            self.voice_state is None
            or isinstance(ctx.author, discord.User)
            or ctx.author.voice is None
            or ctx.author.voice.channel is None
        ):
            return
        destination = ctx.author.voice.channel
        if self.voice_state is not None and self.voice_state.voice is not None:
            await self.voice_state.voice.move_to(destination)
            return
        self.voice_state.voice = await destination.connect()

    @commands.command(name="disconnect", aliases=["dc", "leave", "dis"])
    async def _leave(self, ctx: commands.Context, silent: bool = False) -> None:
        """Clears the queue and leaves the voice channel."""
        if not self.voice_state or not self.voice_state.voice:
            if not silent:
                await ctx.send("Not connected to any voice channel.")
            return
        await self.voice_state.stop()
        await self.bot.change_presence(status=discord.Status.idle)
        self.voice_state.cancel()
        self.voice_state = None

    @commands.command(name="nowplaying", aliases=["np"])
    async def _now(self, ctx: commands.Context) -> None:
        """Displays the currently playing song."""
        if self.voice_state is None:
            return
        if self.voice_state.current is not None:
            await ctx.send(embed=self.voice_state.now_playing_embed())
        else:
            await ctx.send("Nothing playing at the moment.")

    @commands.command(name="pause", aliases=["stop"])
    async def _pause(self, ctx: commands.Context) -> None:
        """Pauses the currently playing song."""
        if self.voice_state is None:
            return
        if self.voice_state.voice is None:
            return
        if self.voice_state.is_playing and self.voice_state.voice.is_playing():
            self.voice_state.voice.pause()
            if ctx.message is not None:
                await ctx.message.add_reaction("⏯")

    @commands.command(name="resume", aliases=["re", "res", "continue"])
    async def _resume(self, ctx: commands.Context) -> None:
        """Resumes a currently paused song."""
        if self.voice_state is None or self.voice_state.voice is None:
            return
        if (
            self.voice_state.is_playing is not None
            and self.voice_state.voice.is_paused()
        ):
            self.voice_state.voice.resume()
            if ctx.message is not None:
                await ctx.message.add_reaction("⏯")

    @commands.command(name="clear", aliases=["cl"])
    async def _stop(self, ctx: commands.Context) -> None:
        """Stops playing song and clears the queue."""
        if self.voice_state is None:
            return
        if self.voice_state.voice is None:
            return
        self.voice_state.songs.clear()
        if self.voice_state.is_playing:
            self.voice_state.voice.stop()
            if ctx.message is not None:
                await ctx.message.add_reaction("⏹")

    @commands.command(name="skip", aliases=["next", "s"])
    @commands.has_permissions(administrator=True)
    async def _skip(self, ctx: commands.Context) -> None:
        """Skips a song without vote."""
        if self.voice_state is None:
            return
        if not self.voice_state.is_playing:
            await ctx.send("Not playing any music right now...")
            return
        if ctx.message is not None:
            await ctx.message.add_reaction("⏭")
        self.voice_state.skip()

    @staticmethod
    def voteskip_embed(
        members: list[discord.Member], skip_votes: set[int], votes_needed: int
    ) -> discord.Embed:
        description = ""
        for member in members:
            description += (
                f'{"✅" if member.id in skip_votes else "❌"}   {member.mention}\n'
            )
        embed = discord.Embed(
            title="Voting Status",
            description=description,
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Vote Count", value=f"{len(skip_votes)}/{votes_needed}")

        return embed

    @commands.command(name="voteskip", aliases=["vs"])
    async def _voteskip(self, ctx: commands.Context) -> None:
        """Vote to skip a song.

        The requestor can skip the current song without a vote.
        """
        if (
            self.voice_state is None
            or ctx.guild is None
            or isinstance(ctx.author, discord.User)
            or ctx.author.voice is None
            or ctx.author.voice.channel is None
        ):
            return
        if not self.voice_state.is_playing:
            await ctx.send("Not playing any music right now...")
            return

        voter = ctx.author
        ids_in_vc = list(ctx.author.voice.channel.voice_states.keys())
        if (
            self.configs.voteskip.requester_autoskip
            and self.voice_state.current is not None
            and voter == self.voice_state.current.requester
        ):
            if ctx.message is not None:
                await ctx.message.add_reaction("⏭")
            self.voice_state.skip()
        elif voter.id not in self.voice_state.skip_votes:
            self.voice_state.skip_votes.add(voter.id)
            total_votes = len(self.voice_state.skip_votes)
            if (
                isinstance(ctx.author, discord.User)
                or ctx.author.voice is None
                or voter.id not in ids_in_vc
            ):
                raise commands.CommandError(
                    "You are not connected to any voice channel."
                )
            members = [
                member
                for id in ids_in_vc
                if (member := ctx.guild.get_member(id))
                and member is not None
                and not member.bot
            ]
            if self.configs.voteskip.exclude_idle:
                members = [member for member in members if member.status != "idle"]
            votes_needed = math.ceil(self.configs.voteskip.fraction * len(members))
            if total_votes >= votes_needed:
                if ctx.message is not None:
                    await ctx.message.add_reaction("⏭")
                self.voice_state.skip()
            else:
                await ctx.send(
                    embed=self.voteskip_embed(
                        members, self.voice_state.skip_votes, votes_needed
                    ),
                    delete_after=60 * 10,
                )
        else:
            await ctx.send("You have already voted to skip this song.")

    @commands.command(name="queue", aliases=["q"])
    async def _queue(self, ctx: commands.Context, *, page: int = 1) -> None:
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """
        if self.voice_state is None:
            return

        if len(self.voice_state.songs) == 0:
            await ctx.send("Empty queue.")
            return
        items_per_page = 10
        pages = math.ceil(len(self.voice_state.songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue = ""
        for i, song in enumerate(self.voice_state.songs.slice(start, end), start=start):
            queue += f"`{i + 1}.` {song}\n"
        embed = discord.Embed(
            description=f"**{len(self.voice_state.songs)} tracks:**\n\n{queue}"
        ).set_footer(text=f"Viewing page {page}/{pages}")
        await ctx.send(embed=embed, delete_after=self.configs.delete_queue)

    @commands.command(name="shuffle", aliases=["random"])
    async def _shuffle(self, ctx: commands.Context) -> None:
        """Shuffles the queue."""
        if self.voice_state is None:
            return

        if len(self.voice_state.songs) == 0:
            raise commands.CommandError("Empty queue.")
        self.voice_state.songs.shuffle()
        if ctx.message is not None:
            await ctx.message.add_reaction("✅")

    @commands.command(name="remove", aliases=["rm"])
    async def _remove(self, ctx: commands.Context, index: int) -> None:
        """Removes a song from the queue at a given index."""
        if self.voice_state is None:
            return

        if len(self.voice_state.songs) == 0:
            raise commands.CommandError("Empty queue.")
        self.voice_state.songs.remove(index - 1)
        if ctx.message is not None:
            await ctx.message.add_reaction("✅")

    @commands.command(name="loop")
    async def _loop(self, ctx: commands.Context) -> None:
        """Toggle whether to loop the currently playing song."""
        if self.voice_state is None:
            return

        if not self.voice_state.is_playing:
            raise commands.CommandError("Nothing being played at the moment.")
        # Inverse boolean value to loop and unloop.
        self.voice_state.loop = not self.voice_state.loop
        if ctx.message is not None:
            await ctx.message.add_reaction("✅")

    @commands.command(name="loopqueue", aliases=["lq"])
    async def _loopqueue(self, ctx: commands.Context) -> None:
        """Toggle whether to loop the queue."""
        if self.voice_state is None:
            return

        if not self.voice_state.is_playing:
            raise commands.CommandError("Nothing being played at the moment.")
        # Inverse boolean value to loop and unloop.
        self.voice_state.loopqueue = not self.voice_state.loopqueue
        if ctx.message is not None:
            await ctx.message.add_reaction("✅")

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx: commands.Context, *, search: str) -> None:
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if self.voice_state is None:
            return

        if not self.voice_state.voice:
            await ctx.invoke(self._join)
        async with ctx.typing():
            try:
                _search = Search(search)
                if _search.playlist:
                    futures = await YTDLSource.create_source_playlist(
                        ctx.author, ctx.channel, _search, loop=self.bot.loop
                    )
                else:
                    futures = await YTDLSource.create_source(
                        ctx.author, ctx.channel, _search, loop=self.bot.loop
                    )
            except Exception as e:
                raise commands.CommandError(
                    f"An error occurred while processing this request: {str(e)}"
                )
            else:
                for future in futures:
                    song = Song.create_pending(future)
                    await self.voice_state.songs.put(song)
                await ctx.invoke(self._queue)

    @commands.command(name="move", aliases=["m", "mv"])
    async def _move(self, ctx: commands.Context, index_from: int, index_to: int):
        """Moves a song from the queue at a given index to a given index."""
        if self.voice_state is None:
            return
        if index_to != index_from:
            self.voice_state.songs.move(index_from - 1, index_to - 1)
        if ctx.message is not None:
            await ctx.message.add_reaction("✅")

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context) -> None:
        if isinstance(ctx.author, discord.User):
            return
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You are not connected to any voice channel.")
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("Bot is already in a voice channel.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Music(bot, CONFIGS.cogs.youtube),
        guilds=[discord.Object(id=CONFIGS.guild_id)],
    )
