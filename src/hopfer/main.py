import logging
import multiprocessing
import os
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase, QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from hopfer import VERSION
from hopfer.bridge.bridge import Bridge
from hopfer.bridge.image_provider import ImageProvider
from hopfer.core.config_object import Config
from hopfer.core.daemon import Daemon
from hopfer.helpers.config import update_config
from hopfer.helpers.logfile import get_handlers
from hopfer.helpers.parse import parse_args

# Block the portal for any child process before they are born
if "-c" in sys.argv or "--multiprocessing-fork" in sys.argv:
    os.environ["QT_NO_XDG_DESKTOP_PORTAL"] = "1"
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

LOG_FORMAT = "%(asctime)s [MAIN] %(levelname)s: %(message)s"

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui"

ICON_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "MaterialSymbols.ttf")
UI_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "JetBrainsMono.ttf")

WINDOW_ICON_PATH = os.fspath(UI_PATH / "Assets" / "hopfer.png")


def main():
    args = parse_args(VERSION)

    logger = logging.getLogger("hopfer")

    handlers = get_handlers(args.logfile)

    LOG_LEVEL = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt="%H:%M:%S",
        handlers=handlers,
    )

    if LOG_LEVEL:
        logger.debug(f"Hopfer {VERSION} starting in DEBUG mode")

    # setup the queues and daemon here. since python v3.14 spawn is the default method, also it is the only one available on windows. if the daemon is initialized in the bridge, qt throws dbus warnings. therefore i've decided to move the daemon initialization here. also, its a bit cleaner to start it here instead of the brdige.

    # TODO: Qt warning do not disappear. investigate further.

    # using spawn to be consistent across platforms
    multiprocessing.set_start_method("spawn", force=True)

    # the request queue
    req_queue = multiprocessing.Queue()
    # the response queue
    res_queue = multiprocessing.Queue()

    # passing them to the bridge as a tuple to save on argument spam.
    queues = (req_queue, res_queue)

    daemon = Daemon(queues=queues)

    daemon_process = multiprocessing.Process(
        target=daemon.run, kwargs={"debug": args.debug}, daemon=False
    )
    daemon_process.start()

    logging.debug("Started daemon process")

    # this is just a merged, cleaned and updated dict
    config_dict = update_config(args.clean)
    # this is the actual object used for two-way sync between the bidge and ui
    config_obj = Config(config_dict)

    app = QGuiApplication(sys.argv)

    app.setIcon(QIcon(WINDOW_ICON_PATH))

    app.setDesktopFileName("hopfer")

    platform = app.platformName()
    logger.debug(f"Running on {platform}")

    icon_font_id = QFontDatabase.addApplicationFont(ICON_FONT_PATH)
    if icon_font_id == -1:
        logger.warning("Failed to load Material Icons")
    else:
        logger.debug("Material Icons loaded successfully.")
        families = QFontDatabase.applicationFontFamilies(icon_font_id)
        logger.debug(f"Material Icons loaded as: {families[0]}")

    # Load UI Font
    ui_font_id = QFontDatabase.addApplicationFont(UI_FONT_PATH)
    if ui_font_id == -1:
        logger.warning("Failed to load JetBrains Mono")
    else:
        logger.debug("JetBrains Mono loaded successfully.")

    engine = QQmlApplicationEngine()

    image_provider = ImageProvider()

    bridge = Bridge(image_provider, config_obj, queues)

    engine.addImageProvider("preview", image_provider)

    engine.rootContext().setContextProperty("bridge", bridge)

    engine.rootContext().setContextProperty("config", config_obj)

    engine.addImportPath(os.fspath(UI_PATH))

    main_qml = UI_PATH / "main.qml"
    engine.load(os.fspath(main_qml))

    def cleanup():
        bridge.exit()
        logging.debug("Closed bridge.")
        if daemon_process.is_alive():
            daemon_process.join()
            logging.debug("Joined daemon.")

    app.aboutToQuit.connect(cleanup)

    if args.file:
        full_path = os.path.abspath(os.path.expanduser(args.file))
        bridge.open_path(full_path, True)
        # print(f"File argument received: {args.file}")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
