import json
import os

def _get_configs():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    with open(f"{abs_path}/../config.json") as configs:
        return json.load(configs)

CONFIGS = _get_configs()
DISCORD_CONFIGS = CONFIGS["discord"]
COG_CONFIGS = DISCORD_CONFIGS["cogs"]