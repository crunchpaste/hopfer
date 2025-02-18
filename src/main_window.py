import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSplitter,
    QWidget,
)
from qframelesswindow import FramelessMainWindow

from controls.titlebar import HopferTitleBar
from helpers.paths import config_path
from image_processor import ImageProcessor
from image_storage import ImageStorage
from preferences import PreferencesDialog
from sidebar import SideBar
from viewer import PhotoViewer


class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self._initialize_components()
        self._setup_ui()

    def _initialize_components(self):
        """Initialize the storage and processor module."""
        self.storage = ImageStorage(self)
        self.processor = ImageProcessor(self, self.storage)

        self.storage.result_signal.connect(self.display_processed_image)

    def _setup_ui(self):
        """Setup the main window layout and UI components."""

        self.setWindowTitle("hopfer")

        try:
            with open(config_path(), "r") as f:
                config = json.load(f)

            # get the last window size from the config
            w = config["window"]["width"]
            h = config["window"]["height"]
            maximized = config["window"]["maximized"]

        except Exception:
            w = 1200
            h = 800
            maximized = False

        self.resize(w, h)
        if maximized:
            self.showMaximized()

        self.setTitleBar(HopferTitleBar(self))

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = SideBar(self.processor, self.storage)

        self.viewer = PhotoViewer(self, self.storage)
        self.viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.viewer_controls = ViewerControls(self.viewer)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.viewer)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        main_layout.addWidget(self.splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect preferences button
        p_button = self.sidebar.toolbox.preferences
        p_button.clicked.connect(self.open_preferences)

        self.setMenuWidget(self.titleBar)

        # self.titleBar.raise_()

    def update_progress(self, progress):
        """Update the UI based on progress."""
        print(f"Processing progress: {progress}%")

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec()

    def display_processed_image(self, reset):
        """Display the processed image in the photo viewer."""
        if self.storage.processed_image is not None:
            pixmap = self.storage.get_processed_pixmap()
            self.viewer.setPhoto(pixmap)
            if reset:
                self.viewer.resetView()
                self.viewer._zoom = 0

    def get_focus(self):
        self.activateWindow()
        self.raise_()

    def reset_viewer(self):
        # mostly for taking screencaptures
        self.viewer.reset_to_default()

    def save_settings(self):
        geometry = self.geometry()
        window = {
            "width": geometry.width(),
            "height": geometry.height(),
            "maximized": self.isMaximized(),
        }

        with open(config_path(), "r") as f:
            config = json.load(f)

        config["window"] = window

        with open(config_path(), "w") as f:
            json.dump(config, f, indent=2)

    def closeEvent(self, event):
        print(self.save_settings())
        super().closeEvent(event)
