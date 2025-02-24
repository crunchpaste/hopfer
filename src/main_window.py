import json
from multiprocessing import Manager, Process, Queue, shared_memory
from multiprocessing.managers import SharedMemoryManager

import numpy as np
import SharedArray as sa
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSplitter,
    QWidget,
)
from qframelesswindow import FramelessMainWindow

from controls.titlebar import HopferTitleBar
from daemon import Daemon
from helpers.image_conversion import numpy_to_pixmap
from helpers.paths import config_path
from preferences import PreferencesDialog
from sidebar import SideBar
from viewer import PhotoViewer


class QueueReader(QObject):
    received_arrays = Signal(bool)
    received_array = Signal(str, tuple)
    close_shm = Signal()
    received_processed = Signal(str, bool)
    received_notification = Signal(str, int)

    def __init__(self, queue, window=None, interval=50):
        super().__init__()
        self.queue = queue
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(interval)

    def check_queue(self):
        while not self.queue.empty():
            message = self.queue.get()
            print(message)
            if message["type"] == "shared_arrays":
                print("received arrays")
                self.received_arrays.emit(True)
            elif message["type"] == "shared_array":
                name = message["name"]
                size = message["size"]
                self.received_array.emit(name, size)
            elif message["type"] == "close_shm":
                self.close_shm.emit()
            elif message["type"] == "display_image":
                array = message["array"]
                reset = message["reset"]
                self.received_processed.emit(array, reset)
            elif message["type"] == "notification":
                notification = message["notification"]
                duration = message["duration"]
                self.received_notification.emit(notification, duration)

            # self.message_received.emit(message)


class QueueWriter(QObject):
    def __init__(self, queue, window=None):
        super().__init__()
        self.queue = queue
        self.window = window

    def close(self):
        message = {"type": "exit"}
        self.queue.put(message)

    def load_image(self, path):
        message = {"type": "load_image", "path": path}
        self.queue.put(message)
        self.window.display_processing_label(True)

    def save_image(self):
        message = {"type": "save_image"}
        self.queue.put(message)

    def send_rotate(self, cw):
        message = {"type": "rotate", "cw": cw}
        self.queue.put(message)

    def send_flip(self):
        message = {"type": "flip"}
        self.queue.put(message)

    def send_invert(self):
        message = {"type": "invert"}
        self.queue.put(message)

    def send_color(self, color, swatch):
        message = {"type": "change_color", "color": color, "swatch": swatch}
        self.queue.put(message)

    def save_like_preview(self, value):
        message = {"type": "save_like_preview", "value": value}
        self.queue.put(message)

    def send_halftone(self, algorithm, settings):
        message = {
            "type": "halftone_settings",
            "algorithm": algorithm,
            "settings": settings,
        }
        self.queue.put(message)
        self.window.display_processing_label(True)

    def send_grayscale(self, mode, settings):
        message = {
            "type": "grayscale_settings",
            "mode": mode,
            "settings": settings,
        }
        self.queue.put(message)
        self.window.display_processing_label(True)

    def send_enhance(self, settings):
        message = {
            "type": "enhance_settings",
            "settings": settings,
        }
        self.queue.put(message)
        self.window.display_processing_label(True)


class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self._initialize_components()
        self._setup_ui()

    def _initialize_components(self):
        """Initialize the storage and processor module."""

        # the request queue
        self.req_queue = Queue()
        # the response queue
        self.res_queue = Queue()
        # manager for simple values
        self.manager = Manager()
        self.smm = SharedMemoryManager()

        self.paths = self.manager.dict()

        self.paths["image_path"] = None
        self.paths["save_path"] = None

        self.daemon = Daemon(
            response=self.res_queue,
            request=self.req_queue,
            paths=self.paths,
        )

        self.daemon_process = Process(target=self.daemon.run, daemon=False)
        self.daemon_process.start()

        self.reader = QueueReader(self.res_queue, window=self)
        self.reader.received_arrays.connect(self.init_arrays)
        self.reader.received_array.connect(self.init_array)
        self.reader.close_shm.connect(self.close_shm)
        self.reader.received_processed.connect(self.display_processed_image)
        self.reader.received_notification.connect(self.display_notification)
        self.writer = QueueWriter(self.req_queue, window=self)

        # self.reader = QueueReader(self.res_queue)

        # self.storage = ImageStorage(self)
        # self.processor = ImageProcessor(self, self.storage)

        # self.storage.result_signal.connect(self.display_processed_image)

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

        self.sidebar = SideBar(self, writer=self.writer)
        # self.viewer = PhotoViewer(self, self.storage)
        self.viewer = PhotoViewer(self, None)
        self.viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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
        self.titleBar.focus.setFocus()

        # it says its needed in the docs, doesnt seem to actually be
        # self.titleBar.raise_()

    def init_array(self, name, size):
        # print(f"INIT ARRAY: {self.shm_preview.shape}")
        self.shm = shared_memory.SharedMemory(name=name)
        self.shm_preview = np.frombuffer(dtype=np.uint8, buffer=self.shm.buf)
        self.shm_preview = self.shm_preview.reshape(size)
        print(f"ARRAY SIZE: {size}")
        print(self.shm_preview.shape)

    def close_shm(self):
        del self.shm_preview
        self.shm.close()

    def init_arrays(self, value):
        self.shm_preview = sa.attach("shm://gray")
        self.shm_rgb = sa.attach("shm://rgb")
        print(f"INIT ARRAY: {self.shm_preview.shape}")

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec()

    def display_processed_image(self, array, reset=True):
        """Display the processed image in the photo viewer."""
        print(f"DISPLAY IMAGE: {self.shm_preview}")
        if array == "gray":
            pixmap = numpy_to_pixmap(self.shm_preview[:, :, 0])
        elif array == "rgb":
            pixmap = numpy_to_pixmap(self.shm_preview)

        self.viewer.setPhoto(pixmap)
        if reset:
            self.viewer.resetView()
            self.viewer._zoom = 0

        self.display_processing_label(False)

    def display_processing_label(self, state=True):
        self.viewer.labelVisible(state)

    def display_notification(self, notification, duration):
        self.sidebar.notifications.show_notification(notification, duration)

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

    def mousePressEvent(self, event):
        # just clearing the focus as it was quite annoying when trying to
        # use shortcuts while focused on an input field
        super().mousePressEvent(event)
        self.titleBar.focus.setFocus()
        self.clearFocus()

    def closeEvent(self, event):
        print(self.save_settings())
        del self.shm_preview
        self.writer.close()
        self.daemon_process.join()
        super().closeEvent(event)
