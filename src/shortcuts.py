from PySide6.QtGui import QKeySequence, QShortcut


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
        self.open_file_shortcut.activated.connect(
            self.main_window.sidebar.toolbox.open_file_dialog
        )

        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self.main_window)
        self.paste_shortcut.activated.connect(
            self.main_window.storage.load_from_clipboard
        )

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.main_window)
        self.save_shortcut.activated.connect(self.main_window.storage.save_image)

        self.saveas_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self.main_window)
        self.saveas_shortcut.activated.connect(
            self.main_window.sidebar.toolbox.save_file_dialog
        )

        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self.main_window)
        self.copy_shortcut.activated.connect(self.main_window.storage.save_to_clipboard)

        # Navigation
        self.image_shortcut = QShortcut(QKeySequence("Ctrl+I"), self.main_window)
        self.image_shortcut.activated.connect(
            lambda: self.main_window.sidebar.activateTab(0)
        )

        self.halftone_shortcut = QShortcut(QKeySequence("Ctrl+H"), self.main_window)
        self.halftone_shortcut.activated.connect(
            lambda: self.main_window.sidebar.activateTab(1)
        )
        # Image viewer shortcuts
        # Toggles the preview blurring
        self.blur_shortcut = QShortcut(QKeySequence("Ctrl+B"), self.main_window)
        self.blur_shortcut.activated.connect(self.main_window.viewer.toggleBlur)
        # Fit the image to the viewer size. This is Ctrl+Zero, not Ctrl+O
        self.fit_shortcut = QShortcut(self.main_window)
        self.fit_shortcut.setKeys([QKeySequence("Ctrl+0"), QKeySequence("0")])
        self.fit_shortcut.activated.connect(self.main_window.viewer.resetView)
        # Preview the image in its original size
        self.x1_shortcut = QShortcut(self.main_window)
        self.x1_shortcut.setKeys([QKeySequence("Ctrl+1"), QKeySequence("1")])
        self.x1_shortcut.activated.connect(self.main_window.viewer.resetOriginal)
        # All the rest of the sizes
        self.x2_shortcut = QShortcut(self.main_window)
        self.x2_shortcut.setKeys([QKeySequence("Ctrl+2"), QKeySequence("2")])
        self.x2_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(2)
        )

        self.x3_shortcut = QShortcut(self.main_window)
        self.x3_shortcut.setKeys([QKeySequence("Ctrl+3"), QKeySequence("3")])
        self.x3_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(3)
        )

        self.x4_shortcut = QShortcut(self.main_window)
        self.x4_shortcut.setKeys([QKeySequence("Ctrl+4"), QKeySequence("4")])
        self.x4_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(4)
        )

        self.x5_shortcut = QShortcut(self.main_window)
        self.x5_shortcut.setKeys([QKeySequence("Ctrl+5"), QKeySequence("5")])
        self.x5_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(5)
        )

        self.x6_shortcut = QShortcut(self.main_window)
        self.x6_shortcut.setKeys([QKeySequence("Ctrl+6"), QKeySequence("6")])
        self.x6_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(6)
        )

        self.x7_shortcut = QShortcut(self.main_window)
        self.x7_shortcut.setKeys([QKeySequence("Ctrl+7"), QKeySequence("7")])
        self.x7_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(7)
        )

        self.x8_shortcut = QShortcut(self.main_window)
        self.x8_shortcut.setKeys([QKeySequence("Ctrl+8"), QKeySequence("8")])
        self.x8_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(8)
        )

        self.x9_shortcut = QShortcut(self.main_window)
        self.x9_shortcut.setKeys([QKeySequence("Ctrl+9"), QKeySequence("9")])
        self.x9_shortcut.activated.connect(
            lambda: self.main_window.viewer.resetToScale(9)
        )

        print("Shortcuts initialized successfully!")
