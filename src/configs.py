import json
import os
from dataclasses import dataclass
from typing import Dict


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
    cogs: Dict[str, CogConfig]


def _get_configs():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    raw_json = {}
    with open(f"{abs_path}/../config.json") as configs:
        raw_json = json.load(configs)
    for key in raw_json["cogs"]:
        raw_json["cogs"][key] = CogConfig(**raw_json["cogs"][key])
    return Configs(**raw_json)


CONFIGS = _get_configs()


if __name__ == "__main__":
    print(CONFIGS)
