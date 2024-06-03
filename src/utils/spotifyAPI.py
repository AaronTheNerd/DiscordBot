from typing import Any

import requests


class AlbumResponse:
    def __init__(self, tracks: dict[str, Any], *args, **kwargs) -> None:
        self.tracks = tracks


class TrackResponse:
    def __init__(
        self, name: str, artists: list[dict[str, Any]], *args, **kwargs
    ) -> None:
        self.name = name
        self.artists = artists


class PlaylistResponse:
    def __init__(self, tracks: dict[str, Any], *args, **kwargs) -> None:
        self.tracks = tracks


class SpotifyAPI:
    auth_url: str = "https://accounts.spotify.com/api/token"
    base_url: str = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str) -> None:
        token = requests.post(
            self.auth_url,
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        ).json()["access_token"]
        self._headers = {"Authorization": f"Bearer {token}"}

    def get_track(self, id: str) -> TrackResponse:
        return TrackResponse(
            **requests.get(f"{self.base_url}/tracks/{id}", headers=self._headers).json()
        )

    def get_playlist(self, id: str, next: str = None) -> PlaylistResponse:
        url = f"{self.base_url}/playlists/{id}"
        is_next_search = False
        if next != None:
            url = next
            is_next_search = True
        raw_response = requests.get(url, headers=self._headers).json()
        if (is_next_search):
            return PlaylistResponse(raw_response)
        return PlaylistResponse(**raw_response)

    def get_album(self, id: str) -> AlbumResponse:
        return AlbumResponse(
            **requests.get(f"{self.base_url}/albums/{id}", headers=self._headers).json()
        )
