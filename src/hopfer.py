import json
import os
import subprocess
import sys
import time

from platformdirs import user_config_dir, user_pictures_dir
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication
from setproctitle import setproctitle

from helpers.load_stylesheet import load_qss
from helpers.no_outline import NoFocusProxyStyle
from main_window import MainWindow
from res_loader import create_desktop_file, get_path
from shortcuts import Shortcuts


def setup_linux_icon():
    """
    This is a hacky workaround to get a somewhat pretty icon in a dock, panel or taskbar on Linux, as noting else seemed to work.
    """
    binary_path = get_path(".")
    icon_path = get_path("res/hopfer.png")
    return create_desktop_file(binary_path, icon_path)


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

        print("Loaded Font Family:", font_families[0])  # The actual font name


def get_latest_hash():
    try:
        hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=".", text=True
        ).strip()
        with open(get_path("res/hash.txt"), "w") as file:
            file.write(hash)
        print(f"{hash}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def generate_config_if_none():
    config_folder = os.path.join(user_config_dir(), "hopfer")
    config_path = os.path.join(config_folder, "config.json")

    print(config_path)
    if not os.path.exists(config_path):
        os.makedirs(config_folder, exist_ok=True)
        config = {
            "window": {"width": 1200, "height": 800, "maximized": False},
            "paths": {
                "open_path": user_pictures_dir(),
                "save_path": user_pictures_dir(),
            },
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)


def main():
    """
    TODO: Create a splash screen.
    """

    # desktop_file_path = None
    start = time.perf_counter()

    if not hasattr(sys.modules["__main__"], "__compiled__"):
        # only get the hash if this is not a nuitka compiled binary
        get_latest_hash()

    setup_linux_icon()

    generate_config_if_none()

    # Setup Linux environment if applicable
    # if sys.platform.startswith("linux") or platform.system() == "Linux":
    #     desktop_file_path = setup_linux_icon()

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

    window = MainWindow()
    window.setWindowIcon(QIcon(get_path("res/hopfer.png")))
    window.show()

    Shortcuts(app, window)

    end = time.perf_counter()

    print(f"Boot time: {end - start} seconds")

    if len(sys.argv) > 1:
        # sys.argv[0] is the script/executable path, sys.argv[1] is the first argument
        path = sys.argv[1]
        window.writer.load_image(path)
        print(f"File passed via CLI/File Manager: {path}")
    else:
        print("No file passed")

    sys.exit(app.exec())
    # pass
    #     # Delete the .desktop file. Suitable only for portable versions and should be improved.
    #     if desktop_file_path and os.path.exists(desktop_file_path):
    #         os.remove(desktop_file_path)
    #         print(f".desktop file removed: {desktop_file_path}")


if __name__ == "__main__":
    setproctitle("hopfer")
    main()
