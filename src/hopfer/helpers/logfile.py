import logging
import os
import sys


def get_handlers(path):
    handlers = [logging.StreamHandler(sys.stdout)]
    if not path:
        return handlers

    try:
        full_path = os.path.abspath(os.path.expanduser(path))
        log_dir = os.path.dirname(full_path)

        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        handlers.append(logging.FileHandler(full_path))
        print(handlers)
        return handlers
    except Exception:
        return handlers
