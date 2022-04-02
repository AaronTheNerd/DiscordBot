import json
import os
from dataclasses import dataclass, field, InitVar
from typing import Dict, Any


class CogConfig:
    def __init__(self, **kwargs):
        self.enabled = kwargs["enabled"]
        self.configs = kwargs
        del self.configs["enabled"]

    def __repr__(self):
        return f"CogConfig(enabled={self.enabled}, configs=Dict[{self.configs}])"

    def __getitem__(self, key):
        return self.configs[key]


@dataclass(frozen=True)
class Configs:
    token: str
    command_prefix: str
    case_insensitive: bool
    cogs: Dict[str, CogConfig] = field(init=False, default_factory=dict)
    _raw_cogs: InitVar[Dict[str, Any]]

    def __post_init__(self, _raw_cogs: Dict[str, Any]):
        for key, val in _raw_cogs.items():
            self.cogs[key] = CogConfig(**val)


def _get_configs():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    with open(f"{abs_path}/../config.json") as configs:
        raw_json = json.load(configs)
        raw_json["discord"]["_raw_cogs"] = raw_json["discord"].pop("cogs")
        return raw_json


CONFIGS = Configs(**(_get_configs()["discord"]))


if __name__ == "__main__":
    print(CONFIGS)