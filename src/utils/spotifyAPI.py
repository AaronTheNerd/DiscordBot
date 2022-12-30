from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests


@dataclass
class AlbumResponse:
    album_type: str
    artists: List[Dict[str, Any]]
    available_markets: List[str]
    copyrights: List[Dict[str, Any]]
    external_ids: Dict[str, Any]
    external_urls: Dict[str, Any]
    genres: List[Any]
    href: str
    id: str
    images: List[Dict[str, Any]]
    label: str
    name: str
    popularity: int
    release_date: str
    release_date_precision: str
    total_tracks: int
    track: Any
    tracks: Dict[str, Any]
    type: str
    uri: str


@dataclass
class TrackResponse:
    album: Dict[str, Any]
    artists: List[Dict[str, Any]]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: Any
    external_urls: Dict[str, Any]
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: str
    track_number: int
    type: str
    uri: str
    is_playable: bool = field(default=False)
    linked_from: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaylistResponse:
    collaborative: bool
    description: str
    external_urls: Dict[str, Any]
    followers: Dict[str, Any]
    href: str
    id: str
    images: List[Dict[str, Any]]
    name: str
    owner: Dict[str, Any]
    primary_color: Any
    public: bool
    snapshot_id: str
    tracks: Dict[str, Any]
    type: str
    uri: str


class SpotifyAPI:
    auth_url: str = "https://accounts.spotify.com/api/token"
    base_url: str = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str) -> None:
        token = requests.post(self.auth_url, {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }).json()["access_token"]
        self._headers = {"Authorization": f"Bearer {token}"}

    def get_track(self, id: str) -> TrackResponse:
        return TrackResponse(
            **requests.get(f"{self.base_url}/tracks/{id}", headers=self._headers).json()
        )

    def get_playlist(self, id: str) -> PlaylistResponse:
        return PlaylistResponse(
            **requests.get(f"{self.base_url}/playlists/{id}", headers=self._headers).json()
        )

    def get_album(self, id: str) -> AlbumResponse:
        return AlbumResponse(
            **requests.get(f"{self.base_url}/albums/{id}", headers=self._headers).json()
        )
