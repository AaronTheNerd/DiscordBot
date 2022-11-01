from dataclasses import dataclass, field
from typing import Dict, List
from urllib.parse import ParseResult, parse_qsl, urlparse

from configs import CONFIGS

from utils.spotifyAPI import PlaylistResponse, SpotifyAPI, TrackResponse


@dataclass
class Search:
    search: str
    searches: List[str] = field(default_factory=list, init=False)
    playlist: bool = field(default=False, init=False)

    def __post_init__(self):
        self.searches = [self.search]
        try:
            parse_result: ParseResult = urlparse(self.search)
        except Exception:
            return
        path: List[str] = parse_result.path.split("/")
        if len(path) < 2:
            return
        if parse_result.netloc == "www.youtube.com":
            if path[1] == "watch":
                queries: Dict[str, str] = dict(parse_qsl(parse_result.query))
                self.searches = [f"youtube.com/watch?v={queries['v']}"]
            elif path[1] == "shorts":
                self.searches = [f"youtube.com/watch?v={path[2]}"]
            elif path[1] == "playlist":
                queries: Dict[str, str] = dict(parse_qsl(parse_result.query))
                self.searches = [f"youtube.com/playlist?list={queries['list']}"]
                self.playlist = True
        elif parse_result.netloc == "youtu.be":
            self.searches = [f"youtube.com/watch?v={path[1]}"]
        elif parse_result.netloc == "open.spotify.com":
            api = SpotifyAPI(CONFIGS.spotify_token)
            if path[1] == "playlist":
                t_resp: TrackResponse = api.get_track(path[2])
                self.searches = [f"{t_resp.name} by {t_resp.artists[0]['name']}"]
            elif path[1] == "track":
                pl_resp: PlaylistResponse = api.get_playlist(path[2])
                self.searches = [
                    f"{track['track']['name']} by {track['track']['artists'][0]['name']}"
                    for track in pl_resp.tracks["items"]
                ]
