import platformdirs
import os
import json
from hopfer import VERSION

DEFAULT_CONFIG = {
    "version": VERSION,
    "window": {
        "x": 0,
        "y": 0,
        "width": 1200,
        "height": 800,
        "maximized": False,
        "native_frame": False,
        "sidebar_width": 400,
    },
    "style": {
        # using an int here despite the headaches, as i plan on adding a neutral theme.
        "theme": 0,
        "accent": 0,
        # to be used in the future
        "font_size": 11,
    },
    "options": {
        # to be used in the future
        "short_shortcuts": False,
        "low_memory": False,
    },
    "paths": {
        "open_path": platformdirs.user_pictures_dir(),
        "save_path": platformdirs.user_pictures_dir(),
        # TODO: Connect these
        "remember_open": True,
        "remember_save": False,
    },
}

CONFIG_FOLDER = os.path.join(platformdirs.user_config_dir(), "hopfer")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "config.json")


def update_config(clean=False):
    os.makedirs(CONFIG_FOLDER, exist_ok=True)

    config_to_write = DEFAULT_CONFIG.copy()

    if clean:
        return config_to_write

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                existing_config = json.load(f)

            config_to_write = _recursive_merge_defaults(existing_config, DEFAULT_CONFIG)

            config_to_write["version"] = DEFAULT_CONFIG["version"]

        except json.JSONDecodeError:
            print(
                f"Warning: Configuration file at {CONFIG_PATH} is invalid. Overwriting with defaults."
            )
        except Exception as e:
            print(f"Error loading config file: {e}. Overwriting with defaults.")

    with open(CONFIG_PATH, "w") as f:
        json.dump(config_to_write, f, indent=2)

    return config_to_write


def get_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        data = json.dumps(config, indent=2)

        with open(CONFIG_PATH, "w") as f:
            f.write(data)

        return True
    except Exception:
        return False


def _recursive_merge_defaults(target_dict, defaults):
    for k, v in defaults.items():
        if k not in target_dict:
            target_dict[k] = v
        elif isinstance(target_dict[k], dict) and isinstance(v, dict):
            target_dict[k] = _recursive_merge_defaults(target_dict[k], v)
    return target_dict
