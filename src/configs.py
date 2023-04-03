import json
import os
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Type, TypeVar


@dataclass
class BindingConfig:
    enabled: bool
    channel_id: int = field(default=-1)


@dataclass
class DnDConfig:
    enabled: bool
    binding: BindingConfig


@dataclass
class RoleOnJoin:
    enabled: bool
    role_id: int


@dataclass
class RandomInsult:
    enabled: bool
    delete_after: int
    insult_chance: float
    adjective_chance: float
    adjectives: list[str]
    insults: list[str]


@dataclass
class EventsConfig:
    enabled: bool
    binding: BindingConfig
    role_on_join: RoleOnJoin
    random_insult_on_command: RandomInsult


@dataclass
class MiscConfig:
    enabled: bool
    binding: BindingConfig


@dataclass
class VoteSkipConfigs:
    exclude_idle: bool
    requester_autoskip: bool
    fraction: float


@dataclass
class YoutubeConfig:
    enabled: bool
    binding: BindingConfig
    voteskip: VoteSkipConfigs
    disconnect_timeout: int
    lazy_load: int
    max_lazy_load: int
    delete_queue: int


@dataclass
class AvailableCogs:
    dnd: DnDConfig
    events: EventsConfig
    misc: MiscConfig
    youtube: YoutubeConfig


@dataclass
class SpotifyAuthConfigs:
    client_id: str
    client_secret: str = field(repr=False)


@dataclass
class Configs:
    token: str = field(repr=False)
    app_id: int = field(repr=False)
    dev_id: int = field(repr=False)
    guild_id: int = field(repr=False)
    command_prefix: str
    case_insensitive: bool
    spotify: SpotifyAuthConfigs
    cogs: AvailableCogs


T = TypeVar("T")


def _replaceWithDataclass(raw_configs: dict[str, Any], cls: Type[T]) -> T:
    for field in fields(cls):
        if is_dataclass(field.type):
            raw_configs[field.name] = _replaceWithDataclass(
                raw_configs[field.name], field.type
            )
    return cls(**raw_configs)


def _getConfigs() -> Configs:
    abs_path = os.path.abspath(os.path.dirname(__file__))
    raw_json = {}
    with open(f"{abs_path}/../config.json") as configs:
        raw_json = json.load(configs)
    return _replaceWithDataclass(raw_json, Configs)


CONFIGS = _getConfigs()


if __name__ == "__main__":
    print(CONFIGS)
