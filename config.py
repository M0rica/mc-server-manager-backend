import json
import os

config = {}


def load_config():
    global config
    if os.path.isfile("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
    else:
        config = get_default_config()


def get_config():
    return config


def get_default_config():
    return {
        "bukkit": {
            "path": "bukkit",
        }
    }


def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f)
