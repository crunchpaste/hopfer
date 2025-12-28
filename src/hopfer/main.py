import os
import sys
from pathlib import Path

from hopfer.bridge.image_provider import ImageProvider
from hopfer.bridge.bridge import Bridge
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
# os.environ["QSG_RENDER_LOOP"] = "basic"

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "ui"

ICON_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "MaterialSymbols.ttf")
UI_FONT_PATH = os.fspath(UI_PATH / "Fonts" / "JetBrainsMono.ttf")

# ICON_FONT_PATH = os.fspath(RES_DIR / "MaterialSymbols.ttf")
# ICON_FONT_FAMILY = "Material Symbols"

# UI_FONT_PATH = os.fspath(RES_DIR / "JetBrainsMono.ttf")
# UI_FONT_FAMILY = "Jetbrains Mono"


def main():
    app = QGuiApplication(sys.argv)

    app.setDesktopFileName("hopfer")

    platform = app.platformName()
    if platform == "wayland":
        print("Running on Wayland")
    elif platform == "xcb":
        print("Running on X11")
    print(platform)

    font_id = QFontDatabase.addApplicationFont(ICON_FONT_PATH)
    font_id = QFontDatabase.addApplicationFont(UI_FONT_PATH)

    if font_id == -1:
        print(f"ERROR: Could not load font from {ICON_FONT_PATH}. Check file path.")
        sys.exit(-1)

    engine = QQmlApplicationEngine()

    image_provider = ImageProvider()

    bridge = Bridge(image_provider)

    engine.addImageProvider("preview", image_provider)

    engine.rootContext().setContextProperty("bridge", bridge)

    engine.addImportPath(os.fspath(UI_PATH))

    main_qml = UI_PATH / "main.qml"
    engine.load(os.fspath(main_qml))

    app.aboutToQuit.connect(bridge.exit)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
