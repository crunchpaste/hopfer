import os
import sys
import platform

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtCore import Qt, QCoreApplication

from main_window import MainWindow
from shortcuts import Shortcuts
from helpers.load_stylesheet import load_qss
from res_loader import get_path, create_desktop_file

def setup_linux_icon():
    """
    This is a hacky workaround to get a somewhat pretty icon in a dock, panel or taskbar on Linux, as noting else seemed to work.
    """
    binary_path = get_path(".")
    icon_path = get_path("res/hopfer.png")
    return create_desktop_file(binary_path, icon_path)

def load_font(app):
    """
    Load a custom font for the application and set it as the default font.
    """
    font_path = get_path("res/fonts/JetBrainsMono.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Failed to load font!")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 14))

def main():
    """
    The main loop.
    TODO: Create a splash screen.
    """
    desktop_file_path = None

    # Setup Linux environment if applicable
    if sys.platform.startswith('linux') or platform.system() == "Linux":
        desktop_file_path = setup_linux_icon()

    # AA_DontUseNativeDialogs is used for custom styling of the Open File Dialog. Not yet stiled.
    # QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_path("res/hopfer.png")))

    # Load resources and configurations
    load_font(app)
    # In ths case a .css file is used insread of .qss as it easier to highlight in an editor.
    load_qss(app, get_path("res/styles/style.css"))

    # Initialize main components
    window = MainWindow()
    window.setWindowIcon(QIcon(get_path("res/hopfer.png")))
    shortcuts = Shortcuts(app, window)
    window.show()

    # Run the application and clean up
    try:
        sys.exit(app.exec())
    finally:
        # Delete the .desktop file. Suitable only for portable versions and should be improved.
        if desktop_file_path and os.path.exists(desktop_file_path):
            os.remove(desktop_file_path)
            print(f".desktop file removed: {desktop_file_path}")

if __name__ == "__main__":
    main()
