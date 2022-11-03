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
    is_url: bool = field(default=False, init=False)

    youtube_url: str = field(default="https://www.youtube.com", init=False)

    def __post_init__(self) -> None:
        self.searches = [self.search]
        try:
            parse_result: ParseResult = urlparse(self.search)
        except Exception:
            return
        path: List[str] = parse_result.path.split("/")
        if len(path) < 2:
            return
        self.is_url = True
        if parse_result.netloc in ["www.youtube.com", "youtube.com"] or (
            parse_result.netloc == "" and parse_result.path[0] in ["www.youtube.com", "youtube.com"]
        ):
            if path[1] == "watch":
                queries: Dict[str, str] = dict(parse_qsl(parse_result.query))
                self.searches = [f"{self.youtube_url}/watch?v={queries['v']}"]
            elif path[1] == "shorts":
                self.searches = [f"{self.youtube_url}/watch?v={path[2]}"]
            elif path[1] == "playlist":
                queries: Dict[str, str] = dict(parse_qsl(parse_result.query))
                self.searches = [f"{self.youtube_url}/playlist?list={queries['list']}"]
                self.playlist = True
        elif parse_result.netloc == "youtu.be" or (
            parse_result.netloc == "" and parse_result.path[0] == "youtu.be"
        ):
            self.searches = [f"{self.youtube_url}/watch?v={path[1]}"]
        elif parse_result.netloc == "open.spotify.com" or (
            parse_result.netloc == "" and parse_result.path[0] == "open.spotify.com"
        ):
            self.is_url = False
            api = SpotifyAPI(CONFIGS.spotify.client_id, CONFIGS.spotify.client_secret)
            if path[1] == "track":
                t_resp: TrackResponse = api.get_track(path[2])
                self.searches = [f"{t_resp.name} by {t_resp.artists[0]['name']}"]
            elif path[1] == "playlist":
                pl_resp: PlaylistResponse = api.get_playlist(path[2])
                self.searches = [
                    f"{track['track']['name']} by {track['track']['artists'][0]['name']}"
                    for track in pl_resp.tracks["items"]
                ]
        self.is_url = False


if __name__ == "__main__":
    TESTS = [
        "https://open.spotify.com/playlist/3ppjI6y3eX9WrYecZZUXWi",
        "open.spotify.com/playlist/3ppjI6y3eX9WrYecZZUXWi",
        "https://www.youtube.com/watch?v=c189ArVQ3k4",
        "www.youtube.com/watch?v=c189ArVQ3k4",
        "https://youtube.com/watch?v=c189ArVQ3k4",
        "youtube.com/watch?v=c189ArVQ3k4",
        "https://www.youtube.com/shorts/l4QjgKJDJjM",
        "www.youtube.com/shorts/l4QjgKJDJjM",
        "https://youtube.com/shorts/l4QjgKJDJjM",
        "youtube.com/shorts/l4QjgKJDJjM",
        "https://www.youtube.com/playlist?list=PLxA687tYuMWi8OUus77n7ZiquRq0Wlbl2",
        "www.youtube.com/playlist?list=PLxA687tYuMWi8OUus77n7ZiquRq0Wlbl2",
        "https://youtube.com/playlist?list=PLxA687tYuMWi8OUus77n7ZiquRq0Wlbl2",
        "youtube.com/playlist?list=PLxA687tYuMWi8OUus77n7ZiquRq0Wlbl2",
        "https://youtu.be/7K1KIsHp-P4"
        "youtu.be/7K1KIsHp-P4"
    ]
    for test in TESTS:
        search = Search(test)
        print(f"Search: {search.searches}, {search.playlist}")
