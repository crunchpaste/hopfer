from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

class Shortcuts:
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window
        self._create_shortcuts()

    def _create_shortcuts(self):
        """Define all shortcuts here."""
        # Example: Global shortcut for opening a file
        self.open_file_shortcut = QShortcut(QKeySequence("Ctrl+O"), self.main_window)
        self.open_file_shortcut.activated.connect(self.main_window.sidebar.toolbox.open_file_dialog)

        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.main_window)
        self.quit_shortcut.activated.connect(self.app.quit)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.main_window)
        self.save_shortcut.activated.connect(self.main_window.storage.save_image)

        print("Shortcuts initialized successfully!")
