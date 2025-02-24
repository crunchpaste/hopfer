from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Toolbox(QWidget):
    def __init__(self, writer=None, main_window=None):
        super().__init__()

        # self.storage = ImageStorage(self)
        self.writer = writer

        self.main_window = main_window
        self.paths = self.main_window.paths

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
        self.open = self._create_button(
            "e43e", "Open image", self.open_file_dialog
        )

        self.save = self._create_button(
            "e161", "Save image", self.writer.save_image
        )
        self.save.setEnabled(False)  # Initial state is disabled

        self.saveas = self._create_button(
            "eb60", "Save as", self.save_file_dialog
        )
        self.saveas.setEnabled(False)  # Initial state is disabled

        # # Image buttons

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
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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

        image_path = self.main_window.paths["image_path"]
        print(image_path)

        if image_path is None:
            origin = ""
        else:
            origin = image_path

        file_path, _ = file_dialog.getOpenFileName(
            None, "Open File", origin, file_filter
        )

        if file_path:
            self.writer.load_image(file_path)

    def save_file_dialog(self):
        """This method is called when the button is clicked to open a file dialog."""
        if self.paths["image_path"] is not None:
            file_dialog = QFileDialog(self)
            options = QFileDialog.Options()
            options |= QFileDialog.DontConfirmOverwrite

            if self.paths["save_path"] is None:
                origin = ""
            else:
                origin = self.paths["save_path"]

            file_filter = (
                "Image Files (*.bmp *.gif *.im *.jpeg *.jpg *.jpe *.jfif "
                "*.jpeg2000 *.jp2 *.png *.tiff *.tif *.webp);;All Files (*)"
            )

            file_path, _ = file_dialog.getSaveFileName(
                None, "Save File", origin, file_filter, options=options
            )

            if file_path:
                self.paths["save_path"] = file_path

                if self.paths["image_path"] != file_path:
                    self.paths["save_path_edited"] = True
                else:
                    self.paths["save_path_edited"] = False

                self.writer.save_image()
        else:
            # This is just so that an error pops in the notification pane.
            # self.storage.save_image()
            self.writer.save_image()

    def _rotate(self, cw):
        self.writer.send_rotate(cw)

    def _flip(self):
        self.writer.send_flip()

    def _invert(self):
        self.writer.send_invert()

    def enable_buttons(self, state):
        """Enables the buttons when an image is available"""
        self.save.setEnabled(state)
        self.saveas.setEnabled(state)
        self.rot_cw.setEnabled(state)
        self.rot_ccw.setEnabled(state)
        self.flip.setEnabled(state)
        self.invert.setEnabled(state)
