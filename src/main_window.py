from PySide6.QtWidgets import QMainWindow, QSplitter, QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget, QPushButton
from PySide6.QtCore import Qt
from sidebar import SideBar
from viewer import PhotoViewer
from viewer_controls import ViewerControls
from image_processor import ImageProcessor
from image_storage import ImageStorage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialize_components()
        self._setup_ui()

    def _initialize_components(self):
        """Initialize the storage and processor module."""
        current_algorithm = "None"
        current_settings = {}
        self.storage = ImageStorage(self)
        self.processor = ImageProcessor(self.storage)

        self.storage.result_signal.connect(self.display_processed_image)

    def _setup_ui(self):
        """Setup the main window layout and UI components."""
        self.setWindowTitle("hopfer")
        self.resize(1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = SideBar(self.processor, self.storage)

        self.viewer = PhotoViewer()
        self.viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus
        )
        # self.viewer_controls = ViewerControls(self.viewer)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.viewer)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setCollapsible(0, False)

        main_layout.addWidget(self.splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def update_progress(self, progress):
        """Update the UI based on progress."""
        print(f"Processing progress: {progress}%")

    def display_processed_image(self, reset):
        """Display the processed image in the photo viewer."""
        if self.storage.processed_image is not None:
            pixmap = self.storage.get_processed_pixmap()
            self.viewer.setPhoto(pixmap)
            if reset:
                self.viewer.resetView()
                self.viewer._zoom = 0
