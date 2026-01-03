import os
import sys
from pathlib import Path
import argparse
import textwrap
import logging

from hopfer.bridge.image_provider import ImageProvider
from hopfer.bridge.bridge import Bridge
from hopfer.helpers.config import update_config
from hopfer import VERSION
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

LOG_FORMAT = "%(levelname)s: %(message)s"

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui"

ICON_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "MaterialSymbols.ttf")
UI_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "JetBrainsMono.ttf")


def main():
    # desc =
    parser = argparse.ArgumentParser(
        prog="hopfer-qml",
        # description="""GUI for halftoning images. \n Source code: https://github.com/crunchpaste/hopfer"""
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(f"""\
        A specialized toolkit providing experimental halftoning for print.
        Version: {VERSION}

        Supported formats: .jpg, .png, .tiff, .webp, .jp2, .gif, .bmp
        Source code: https://github.com/crunchpaste/hopfer

        Usage: hopfer-qml [options] [file]
        """),
        usage=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="enable debug logging"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument("file", nargs="?", default=None, help=argparse.SUPPRESS)

    args = parser.parse_args()

    logger = logging.getLogger("hopfer")
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    if args.debug:
        logger.debug(f"Hopfer {VERSION} starting in DEBUG mode")

    config = update_config()

    app = QGuiApplication(sys.argv)

    app.setDesktopFileName("hopfer")

    platform = app.platformName()
    logger.debug(f"Running on {platform}")

    icon_font_id = QFontDatabase.addApplicationFont(ICON_FONT_PATH)
    if icon_font_id == -1:
        logger.warning("Failed to load Material Icons")
    else:
        logger.debug("Material Icons loaded successfully.")

    # Load UI Font
    ui_font_id = QFontDatabase.addApplicationFont(UI_FONT_PATH)
    if ui_font_id == -1:
        logger.warning("Failed to load JetBrains Mono")
    else:
        logger.debug("JetBrains Mono loaded successfully.")

    engine = QQmlApplicationEngine()

    image_provider = ImageProvider()

    bridge = Bridge(image_provider)

    engine.addImageProvider("preview", image_provider)

    engine.rootContext().setContextProperty("bridge", bridge)

    engine.rootContext().setContextProperty("config", config)

    engine.addImportPath(os.fspath(UI_PATH))

    main_qml = UI_PATH / "main.qml"
    engine.load(os.fspath(main_qml))

    root_objects = engine.rootObjects()
    window = root_objects[0]
    bridge.set_window(window)

    app.aboutToQuit.connect(bridge.exit)

    if args.file:
        full_path = os.path.abspath(os.path.expanduser(args.file))
        bridge.open_path(full_path)
        # print(f"File argument received: {args.file}")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
