from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Toolbox(QWidget):
    file_opened_signal = Signal()

    def __init__(self, storage):
        super().__init__()

        self.storage = storage

        self.setObjectName("toolbox")  # For QSS styling

        # Create a layout for the toolbox
        self._initialize_ui()

    def _initialize_ui(self):
        toolbox_layout = QVBoxLayout(self)
        toolbox_layout.setContentsMargins(0, 0, 10, 0)  # Adjust margins

        _ext = "svg"

        # Create the buttons
        # Spacer
        spacer0 = QSpacerItem(20, 15)
        spacer1 = QSpacerItem(20, 15)

        # File buttons
        self.open = self._create_button("e43e", "Open image", self.open_file_dialog)

        self.save = self._create_button("e161", "Save image", self.storage.save_image)
        self.save.setEnabled(False)  # Initial state is disabled

        self.saveas = self._create_button("eb60", "Save as", self.save_file_dialog)
        self.saveas.setEnabled(False)  # Initial state is disabled

        # Image buttons

        self.rot_cw = self._create_button("e41a", "Rotate CW", None)
        self.rot_cw.setEnabled(False)
        self.rot_cw.clicked.connect(lambda: self._rotate(True))

        self.rot_ccw = self._create_button("e419", "Rotate CCW", None)
        self.rot_ccw.setEnabled(False)
        self.rot_ccw.clicked.connect(lambda: self._rotate(False))

        self.flip = self._create_button("e3e8", "Flip", self._flip)
        self.flip.setEnabled(False)

        self.invert = self._create_button("e891", "Invert colors", self._invert)
        self.invert.setEnabled(False)

        # App buttons

        self.preferences = self._create_button("e8b8", "Preferences", None)
        self.preferences.setObjectName("last-button")

        # Add buttons to layout
        toolbox_layout.addWidget(self.open)
        toolbox_layout.addWidget(self.save)
        toolbox_layout.addWidget(self.saveas)

        toolbox_layout.addItem(spacer0)

        toolbox_layout.addWidget(self.invert)
        toolbox_layout.addWidget(self.rot_cw)
        toolbox_layout.addWidget(self.rot_ccw)
        toolbox_layout.addWidget(self.flip)

        toolbox_layout.addItem(spacer1)

        toolbox_layout.addStretch()
        toolbox_layout.addWidget(self.preferences)

    def _create_button(self, unicode, tooltip, click_handler):
        """
        Creates a button with the specified icons, tooltip, and click handler.

        Args:
            unicode (str): The unicode provided by google fonts
            click_handler (function or None): Function to connect to the button click event.

        Returns:
            QPushButton: The configured QPushButton.
        """
        icon_unicode = chr(int(unicode, 16))
        button = QPushButton(icon_unicode)
        button.setToolTip(tooltip)

        if click_handler:
            button.clicked.connect(click_handler)

        return button

    def open_file_dialog(self):
        """This method is called when the button is clicked to open a file dialog."""
        file_dialog = QFileDialog(self)
        file_filter = (
            "Image Files (*.bmp *.gif *.im *.jpeg *.jpg *.jpe *.jfif "
            "*.jpeg2000 *.jp2 *.png *.tiff *.tif *.webp);;All Files (*)"
        )

        if self.storage.image_path is None:
            origin = ""
        else:
            origin = self.storage.image_path

        file_path, _ = file_dialog.getOpenFileName(
            None, "Open File", origin, file_filter
        )

        if file_path:
            self.storage.load_image(file_path)
            print(f"Selected file: {file_path}")
            self.file_opened_signal.emit()

    def save_file_dialog(self):
        """This method is called when the button is clicked to open a file dialog."""
        if self.storage.image_path is not None:
            file_dialog = QFileDialog(self)

            if self.storage.save_path is None:
                origin = ""
            else:
                origin = self.storage.save_path

            file_filter = (
                "Image Files (*.bmp *.gif *.im *.jpeg *.jpg *.jpe *.jfif "
                "*.jpeg2000 *.jp2 *.png *.tiff *.tif *.webp);;All Files (*)"
            )

            file_path, _ = file_dialog.getSaveFileName(
                None, "Save File", origin, file_filter
            )

            if file_path:
                self.storage.save_path = file_path
                self.storage.save_image()
                # self.file_opened_signal.emit()
        else:
            # This is just so that an error pops in the notification pane.
            self.storage.save_image()

    def _rotate(self, cw):
        self.storage.rotate_image(cw)

    def _flip(self):
        self.storage.flip_image()

    def _invert(self):
        self.storage.invert_image()

    def enable_buttons(self):
        """Enables the buttons when an image is available"""
        self.save.setEnabled(True)
        self.saveas.setEnabled(True)
        self.rot_cw.setEnabled(True)
        self.rot_ccw.setEnabled(True)
        self.flip.setEnabled(True)
        self.invert.setEnabled(True)
