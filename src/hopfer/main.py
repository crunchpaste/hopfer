import logging
import os
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from hopfer import VERSION
from hopfer.bridge.bridge import Bridge
from hopfer.bridge.image_provider import ImageProvider
from hopfer.core.config_object import Config
from hopfer.helpers.config import update_config
from hopfer.helpers.logfile import get_handlers
from hopfer.helpers.parse import parse_args

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui"

ICON_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "MaterialSymbols.ttf")
UI_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "JetBrainsMono.ttf")


def main():
    args = parse_args(VERSION)

    logger = logging.getLogger("hopfer")

    handlers = get_handlers(args.logfile)

    log_level = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    if args.debug:
        logger.debug(f"Hopfer {VERSION} starting in DEBUG mode")

    # this is just a merged, cleaned and updated dict
    config_dict = update_config(args.clean)
    # this is the actual object used for two-way sync between the bidge and ui
    config_obj = Config(config_dict)

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

    bridge = Bridge(image_provider, config_obj)

    engine.addImageProvider("preview", image_provider)

    engine.rootContext().setContextProperty("bridge", bridge)

    engine.rootContext().setContextProperty("config", config_obj)

    engine.addImportPath(os.fspath(UI_PATH))

    main_qml = UI_PATH / "main.qml"
    engine.load(os.fspath(main_qml))

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
