import json
import os
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, TypeVar, Dict, Type


@dataclass(frozen=True)
class CogConfig:
    enabled: bool
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AvailableCogs:
    dnd: CogConfig
    events: CogConfig
    misc: CogConfig
    youtube: CogConfig


@dataclass(frozen=True)
class Configs:
    token: str
    command_prefix: str
    case_insensitive: bool
    spotify_token: str
    cogs: AvailableCogs


T = TypeVar("T")


def _replaceWithDataclass(raw_configs: Dict[str, Any], cls: Type[T]) -> T:
    for field in fields(cls):
        if is_dataclass(field.type):
            raw_configs[field.name] = _replaceWithDataclass(raw_configs[field.name], field.type)
    return cls(**raw_configs)


def _getConfigs():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    raw_json = {}
    with open(f"{abs_path}/../config.json") as configs:
        raw_json = json.load(configs)
    return _replaceWithDataclass(raw_json, Configs)


CONFIGS = _getConfigs()


if __name__ == "__main__":
    print(CONFIGS)
