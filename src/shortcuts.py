from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

class Shortcuts:
    def __init__(self, app, main_window):
        self.app = app
        self.main_window = main_window
        self._create_shortcuts()

    def _create_shortcuts(self):
        """All of the shortcuts used in the app are defined here."""

        # Window shortcuts
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.main_window)
        self.quit_shortcut.activated.connect(self.app.quit)

        # File manipulation
        self.open_file_shortcut = QShortcut(QKeySequence("Ctrl+O"), self.main_window)
        self.open_file_shortcut.activated.connect(self.main_window.sidebar.toolbox.open_file_dialog)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.main_window)
        self.save_shortcut.activated.connect(self.main_window.storage.save_image)

        self.saveas_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self.main_window)
        self.saveas_shortcut.activated.connect(self.main_window.sidebar.toolbox.save_file_dialog)

        # Image viewer shortcuts
        # Fit the image to the viewer size. This is Ctrl+Zero, not Ctrl+O
        self.fit_shortcut = QShortcut(QKeySequence("Ctrl+0"), self.main_window)
        self.fit_shortcut.activated.connect(self.main_window.viewer.resetView)
        # Preview the image in its original size
        self.x1_shortcut = QShortcut(QKeySequence("Ctrl+1"), self.main_window)
        self.x1_shortcut.activated.connect(self.main_window.viewer.resetOriginal)
        # All the rest of the sizes
        self.x2_shortcut = QShortcut(QKeySequence("Ctrl+2"), self.main_window)
        self.x2_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(2))

        self.x3_shortcut = QShortcut(QKeySequence("Ctrl+3"), self.main_window)
        self.x3_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(3))

        self.x4_shortcut = QShortcut(QKeySequence("Ctrl+4"), self.main_window)
        self.x4_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(4))

        self.x5_shortcut = QShortcut(QKeySequence("Ctrl+5"), self.main_window)
        self.x5_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(5))

        self.x6_shortcut = QShortcut(QKeySequence("Ctrl+6"), self.main_window)
        self.x6_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(6))

        self.x7_shortcut = QShortcut(QKeySequence("Ctrl+7"), self.main_window)
        self.x7_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(7))

        self.x8_shortcut = QShortcut(QKeySequence("Ctrl+8"), self.main_window)
        self.x8_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(8))

        self.x9_shortcut = QShortcut(QKeySequence("Ctrl+9"), self.main_window)
        self.x9_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(9))

        print("Shortcuts initialized successfully!")
