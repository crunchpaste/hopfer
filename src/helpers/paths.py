import os

from platformdirs import user_config_dir


def config_folder():
    return os.path.join(user_config_dir(), "hopfer")


def config_path():
    return os.path.join(config_folder(), "config.json")
