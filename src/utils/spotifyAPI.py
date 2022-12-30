from typing import Any, Dict, List

import requests


class AlbumResponse:
    def __init__(self, tracks: Dict[str, Any], *args, **kwargs) -> None:
        self.tracks = tracks


class TrackResponse:
    def __init__(self, name: str, artists: List[Dict[str, Any]], *args, **kwargs) -> None:
        self.name = name
        self.artists = artists


class PlaylistResponse:
    def __init__(self, tracks: Dict[str, Any], *args, **kwargs) -> None:
        self.tracks = tracks


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
