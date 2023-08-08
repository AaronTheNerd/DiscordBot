import json
import os
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Type, TypeVar


def custom_setters(cls):
    for field in fields(cls):
        if not is_dataclass(field.type):

            def wrapper(fld):
                def setter(self, value) -> None:
                    self.__dict__[fld.name] = value
                    CONFIGS.dump()

                return setter

            setattr(cls, f"set_{field.name}", wrapper(field))
    return cls


@custom_setters
@dataclass
class BindingConfig:
    enabled: bool
    channel_id: int = field(default=-1)


@custom_setters
@dataclass
class DnDConfig:
    enabled: bool
    binding: BindingConfig


@custom_setters
@dataclass
class RoleOnJoin:
    enabled: bool
    role_id: int


@custom_setters
@dataclass
class RandomInsult:
    enabled: bool
    delete_after: int
    insult_chance: float
    adjective_chance: float
    adjectives: list[str]
    insults: list[str]


@custom_setters
@dataclass
class EventsConfig:
    enabled: bool
    binding: BindingConfig
    role_on_join: RoleOnJoin
    random_insult_on_command: RandomInsult


@custom_setters
@dataclass
class MiscConfig:
    enabled: bool
    binding: BindingConfig


@custom_setters
@dataclass
class VoteSkipConfigs:
    exclude_idle: bool
    requester_autoskip: bool
    fraction: float


@custom_setters
@dataclass
class YoutubeConfig:
    enabled: bool
    binding: BindingConfig
    voteskip: VoteSkipConfigs
    disconnect_timeout: int
    lazy_load: int
    max_lazy_load: int
    delete_queue: int


@custom_setters
@dataclass
class AvailableCogs:
    dnd: DnDConfig
    events: EventsConfig
    misc: MiscConfig
    youtube: YoutubeConfig


@custom_setters
@dataclass
class SpotifyAuthConfigs:
    client_id: str
    client_secret: str = field(repr=False)


@custom_setters
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

    def dump(self) -> None:
        abs_path = os.path.abspath(os.path.dirname(__file__))
        json_content = _getJson(self)
        with open(f"{abs_path}/../config.json", "w+") as json_file:
            json.dump(json_content, json_file, indent=4)


T = TypeVar("T")


def _replaceWithDataclass(raw_configs: dict[str, Any], cls: Type[T]) -> T:
    for field in fields(cls):
        if is_dataclass(field.type):
            raw_configs[field.name] = _replaceWithDataclass(
                raw_configs[field.name], field.type
            )
    return cls(**raw_configs)


def _getJson(configs) -> dict[str, Any]:
    content = {}
    if not is_dataclass(configs):
        return {}
    for field in fields(configs):
        value = getattr(configs, field.name)
        if is_dataclass(field.type):
            content[field.name] = _getJson(value)
        else:
            content[field.name] = value
    return content


def _getConfigs() -> Configs:
    abs_path = os.path.abspath(os.path.dirname(__file__))
    raw_json = {}
    with open(f"{abs_path}/../config.json") as configs:
        raw_json = json.load(configs)
    return _replaceWithDataclass(raw_json, Configs)


CONFIGS = _getConfigs()


if __name__ == "__main__":
    print(CONFIGS)
    CONFIGS.set_case_insensitive(False)
    CONFIGS.set_command_prefix("/")
    CONFIGS.cogs.youtube.set_enabled(False)
