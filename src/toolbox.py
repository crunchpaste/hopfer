from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal
from res_loader import get_path


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

        icon_path = get_path("res/icons")

        # Create the buttons
        self.open = self._create_button(icon_path + "/open.svg", icon_path + "/dark/open.svg", icon_path + "/salmon/open.svg", "Open image", self.open_file_dialog)
        self.save = self._create_button(icon_path + "/save.svg", icon_path + "/dark/save.svg", icon_path + "/salmon/save.svg", "Save image", self.storage.save_image)
        self.saveas = self._create_button(icon_path + "/save_as.svg", icon_path + "/dark/save_as.svg", icon_path + "/salmon/save_as.svg", "Save as", None)
        self.settings = self._create_button(icon_path + "/settings.svg", icon_path + "/dark/settings.svg", icon_path + "/salmon/settings.svg", "Settings", None)
        self.settings.setObjectName("last-button")
        # Add buttons to layout
        toolbox_layout.addWidget(self.open)
        toolbox_layout.addWidget(self.save)
        toolbox_layout.addWidget(self.saveas)
        toolbox_layout.addStretch()
        toolbox_layout.addWidget(self.settings)

    def _create_button(self, icon_default, icon_hover, icon_focus, tooltip, click_handler):
        """
        Creates a button with the specified icons, tooltip, and click handler.

        Args:
            icon_default (str): Path to the default icon.
            icon_hover (str): Path to the icon on hover.
            icon_focus (str): Path to the icon on focus.
            tooltip (str): Tooltip text for the button.
            click_handler (function or None): Function to connect to the button click event.

        Returns:
            QPushButton: The configured QPushButton.
        """
        button = QPushButton("")
        button.setIcon(QIcon(icon_default))
        button.setIconSize(QSize(30, 30))  # Icon size
        button.setStyleSheet(
            f'QPushButton:hover {{ icon: url({icon_hover}); }}'
            f'QPushButton:focus {{ icon: url({icon_focus}); }}'
        )
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
        file_path, _ = file_dialog.getOpenFileName(None, "Open File", "", file_filter)

        if file_path:
            self.storage.load_image(file_path)
            print(f"Selected file: {file_path}")
            self.file_opened_signal.emit()
