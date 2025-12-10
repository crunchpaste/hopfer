import json
import os
import sys
import time

from platformdirs import user_config_dir, user_pictures_dir
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication
from setproctitle import setproctitle

from helpers.load_stylesheet import load_qss
from helpers.no_outline import NoFocusProxyStyle
from main_window import MainWindow
from res_loader import get_path
from shortcuts import Shortcuts


def load_font(path):
    """
    Load a custom font for the application and set it as the default font.
    """
    font_path = get_path(path)
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id == -1:
        print("Failed to load font!")
    else:
        font_families = QFontDatabase.applicationFontFamilies(font_id)

        font = QFont(font_families[0])

        # It seems that this does nothing to help awful font rendering on Windows
        # The only solution I've found so far is to just use MacType, available at
        # https://mactype.net
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)


# def generate_config_if_none():
#     config_folder = os.path.join(user_config_dir(), "hopfer")
#     config_path = os.path.join(config_folder, "config.json")
#
#     if not os.path.exists(config_path):
#         os.makedirs(config_folder, exist_ok=True)
#         config = {
#             "window": {"width": 1200, "height": 800, "maximized": False},
#             "paths": {
#                 "open_path": user_pictures_dir(),
#                 "save_path": user_pictures_dir(),
#             },
#             "theme": "dark"
#         }
#         with open(config_path, "w") as f:
#             json.dump(config, f, indent=2)


def generate_config_if_none():
    config_folder = os.path.join(user_config_dir(), "hopfer")
    config_path = os.path.join(config_folder, "config.json")

    DEFAULT_CONFIG = {
        "window": {"width": 1200, "height": 800, "maximized": False},
        "paths": {
            "open_path": user_pictures_dir(),
            "save_path": user_pictures_dir(),
        },
        "theme": "dark",
    }

    os.makedirs(config_folder, exist_ok=True)

    config_to_write = DEFAULT_CONFIG.copy()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                existing_config = json.load(f)

            config_to_write = _recursive_merge_defaults(
                existing_config, DEFAULT_CONFIG
            )

        except json.JSONDecodeError:
            print(
                f"Warning: Configuration file at {config_path} is invalid. Overwriting with defaults."
            )
        except Exception as e:
            print(f"Error loading config file: {e}. Overwriting with defaults.")

    with open(config_path, "w") as f:
        json.dump(config_to_write, f, indent=2)


def _recursive_merge_defaults(target_dict, defaults):
    for k, v in defaults.items():
        if k not in target_dict:
            target_dict[k] = v
        elif isinstance(target_dict[k], dict) and isinstance(v, dict):
            target_dict[k] = _recursive_merge_defaults(target_dict[k], v)
    return target_dict


def main():
    """
    TODO: Create a splash screen.
    """

    start = time.perf_counter()

    generate_config_if_none()

    # AA_DontUseNativeDialogs is used for custom styling of
    # the Open File Dialog. Not yet styled.
    # QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_path("res/hopfer.png")))

    load_font("res/fonts/JetBrainsMono.ttf")
    load_font("res/fonts/mat_s/MaterialSymbols.ttf")
    app.setStyle("Fusion")  # Fixes some issues on windows
    app.setStyle(NoFocusProxyStyle())
    # In ths case a .css file is used insread of .qss as it easier to
    # highlight in an editor.
    load_qss(app, get_path("res/styles/style.css"))

    window = MainWindow(app)
    window.setWindowIcon(QIcon(get_path("res/hopfer.png")))
    window.show()

    Shortcuts(app, window)

    end = time.perf_counter()

    # print(f"Boot time: {end - start} seconds")

    if len(sys.argv) > 1:
        # Load an image passed from cli or a file manager
        path = sys.argv[1]
        window.writer.load_image(path)

    sys.exit(app.exec())


if __name__ == "__main__":
    setproctitle("hopfer")
    main()
