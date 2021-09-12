import json
import os

def _get_configs():
    abs_path = os.path.abspath(os.path.dirname(__file__))
    with open(f"{abs_path}/../config.json") as configs:
        return json.load(configs)

CONFIGS = _get_configs()
DISCORD_CONFIGS = CONFIGS["discord"]
COG_CONFIGS = DISCORD_CONFIGS["cogs"]
MISC_COG_CONFIGS = COG_CONFIGS["misc"]
SPOTIFY_COG_CONFIGS = COG_CONFIGS["spotify"]
EVENTS_COG_CONFIGS = COG_CONFIGS["events"]
ROLE_ON_JOIN_CONFIGS = EVENTS_COG_CONFIGS["role_on_join"]
RANDOM_INSULT_CONFIGS = EVENTS_COG_CONFIGS["random_insult_on_command"]
