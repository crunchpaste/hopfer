import json
import pickle
from multiprocessing import Process, SimpleQueue, shared_memory

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QSplitter,
    QWidget,
)
from qframelesswindow import FramelessMainWindow

from controls.resize_dialog import ImageResizeDialog
from controls.titlebar import HopferTitleBar
from daemon import Daemon
from helpers.image_conversion import numpy_to_pixmap, qimage_to_numpy
from helpers.paths import config_path
from preferences import PreferencesDialog
from queue_io import QueueReader, QueueWriter
from sidebar import SideBar
from viewer import PhotoViewer

# this is here for debugging windows multiprocessing issues from linux
# multiprocessing.set_start_method("spawn", force=True)


class MainWindow(FramelessMainWindow):
    """
    Inherits from FramelessMainWindow and is used for the custom toolbar capabilities.
    """

    def __init__(self):
        super().__init__()
        # needed for the resize dialog
        self.w = 1
        self.h = 1
        self.dpi = 150
        self.shm = None
        self.processing = False
        self._initialize_components()
        self._setup_ui()

    def _initialize_components(self):
        # the request queue
        self.req_queue = SimpleQueue()
        # the response queue
        self.res_queue = SimpleQueue()

        self.paths = {"image_path": None, "save_path": None}

        self.daemon = Daemon(response=self.res_queue, request=self.req_queue)

        self.daemon_process = Process(target=self.daemon.run, daemon=False)
        self.daemon_process.start()
        self.shm_preview = None

        self.reader = QueueReader(self.res_queue, window=self)

        # READER SIGNALS
        self.reader.received_array.connect(self.init_array)
        self.reader.close_shm.connect(self.close_shm)
        self.reader.received_processed.connect(self.display_processed_image)
        # windows specific signal as it can't properly deal with shared memory
        self.reader.received_processed_nt.connect(
            self.display_processed_image_nt
        )
        self.reader.received_notification.connect(self.display_notification)
        self.reader.show_processing_label.connect(self.display_processing_label)

        self.writer = QueueWriter(self.req_queue, window=self)

        # WRITER SIGNALS
        self.writer.rotate.connect(self.rotate_shm)

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
        self.shm = shared_memory.SharedMemory(name=name, track=False)
        self.shm_preview = np.frombuffer(dtype=np.uint8, buffer=self.shm.buf)
        self.shm_preview = self.shm_preview.reshape(size)

    def rotate_shm(self, cw):
        if cw:
            self.shm_preview = np.rot90(self.shm_preview, k=-1)
        else:
            self.shm_preview = np.rot90(self.shm_preview, k=1)

    def close_shm(self):
        if self.shm_preview is not None:
            del self.shm_preview
        if self.shm is not None:
            self.shm.close()

    def open_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec()

    def open_resize_dialog(self):
        """
        Creates and executes the dialog, then handles the result.
        """
        if not self.viewer.hasValidPhoto():
            return

        self.dialog = ImageResizeDialog(parent=self)

        if self.dialog.exec() == QDialog.Accepted:
            result = self.dialog.get_result()
            dpi = result["dpi"]
            h = result["height_px"]
            w = result["width_px"]
            interpolation = result["interpolation"]

            self.h = h
            self.w = w
            self.dpi = dpi

            self.writer.resize(w, h, interpolation)
        else:
            pass

    def display_processed_image(self, array, reset=True):
        """Display the processed image in the photo viewer."""
        _img = np.ascontiguousarray(self.shm_preview)
        if array == "gray":
            pixmap = numpy_to_pixmap(_img[:, :, 0])
        elif array == "rgb":
            pixmap = numpy_to_pixmap(_img)

        self.viewer.setPhoto(pixmap)
        if reset:
            self.viewer.resetView()
            self.viewer._zoom = 0

        self.display_processing_label(False)

    def display_processed_image_nt(self, array, reset=True):
        """Display the processed image in the photo viewer on windows."""
        _img = pickle.loads(array)

        pixmap = numpy_to_pixmap(_img)

        self.viewer.setPhoto(pixmap)
        if reset:
            self.viewer.resetView()
            self.viewer._zoom = 0

        self.display_processing_label(False)

    def display_processing_label(self, state=True):
        self.viewer.labelVisible(state)

        if state:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        else:
            while QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()

    def display_notification(self, notification, duration=3000):
        self.sidebar.notifications.show_notification(notification, duration)

    def handle_clipboard(self):
        self.app = QApplication.instance()
        clipboard = self.app.clipboard()

        _image = clipboard.image()
        _url = clipboard.text()

        if not _image.isNull():
            # A much faster way to transfer the image to the daemon
            # than the one proposed at:
            # https://stackoverflow.com/questions/47289884/
            # how-to-convert-qimageqpixmap-to-pil-image-in-python-3

            self.display_processing_label(True)
            _image_np = qimage_to_numpy(_image)

            # using pickle mostly for simplicity as I dont want to deal
            # with shared memory for an operation that happens so rarely.
            pickled_data = pickle.dumps(_image_np)

            self.writer.send_pickled_image(pickled_data)

        elif _url != "":
            self.writer.send_url(_url)

    def store_in_clipboard(self, data):
        image = pickle.loads(data)
        qimage = numpy_to_pixmap(image, qi=True)

        self.app = QApplication.instance()
        clipboard = self.app.clipboard()

        clipboard.setImage(qimage)

        self.display_notification("Image stored in clipboard.")

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
        # print(self.save_settings())
        self.close_shm()
        self.writer.close()
        self.daemon_process.join()
        super().closeEvent(event)
