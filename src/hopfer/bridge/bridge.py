from PySide6.QtCore import QObject, Slot, Signal, QUrl, Property
from PySide6.QtGui import QGuiApplication
from hopfer.core.daemon import Daemon
from hopfer.core.queue_io import QueueReader, QueueWriter
from hopfer.helpers.config import get_config, save_config
from hopfer.helpers.image_conversion import numpy_to_pixmap, qimage_to_numpy
from multiprocessing import SimpleQueue, Process, shared_memory
import pickle
import numpy as np
import json
import platformdirs
import os


class Bridge(QObject):
    processingStarted = Signal()
    resetView = Signal()
    displayImage = Signal()
    loadFailed = Signal()
    showNotification = Signal(str, int)
    enableToolbar = Signal(bool)
    originalGrayscale = Signal(bool)
    pathsChanged = Signal()
    hasImage = Signal(bool)

    def __init__(self, image_provider, parent=None):
        super().__init__(parent)
        self.shm = None
        self.image_provider = image_provider
        self.processing = False
        self._has_image = False

        self.clipboard = QGuiApplication.clipboard()
        self._initial_folder = platformdirs.user_videos_dir()

        self._window = None

        self._init_components()

    def _init_components(self):
        # the request queue
        self.req_queue = SimpleQueue()
        # the response queue
        self.res_queue = SimpleQueue()

        self._paths = {"open_path": None, "save_path": None}

        self.daemon = Daemon(response=self.res_queue, request=self.req_queue)

        self.daemon_process = Process(target=self.daemon.run, daemon=False)
        self.daemon_process.start()
        self.shm_preview = None

        self.reader = QueueReader(self.res_queue, bridge=self)

        # READER SIGNALS
        self.reader.received_array.connect(self.init_array)
        self.reader.close_shm.connect(self.close_shm)
        self.reader.received_processed.connect(self.display_processed_image)
        # windows specific signal as it can't properly deal with shared memory
        # self.reader.received_processed_nt.connect(
        # self.display_processed_image_nt
        # )
        # self.reader.received_notification.connect(self.display_notification)
        # self.reader.show_processing_label.connect(self.display_processing_label)

        self.writer = QueueWriter(self.req_queue, bridge=self)

    def set_window(self, window):
        self._window = window

    @Property(bool, notify=hasImage)
    def has_image(self):
        return self._has_image

    @Property(str)
    def initial_folder_url(self):
        return QUrl.fromLocalFile(self._initial_folder).toString()

    @Slot(str, str)
    def send_grayscale(self, algorithm, settings):
        settings_dict = json.loads(settings)
        self.writer.send_grayscale(algorithm, settings_dict)

    @Slot(str)
    def send_enhance(self, settings):
        settings_dict = json.loads(settings)
        self.writer.send_enhance(settings_dict)

    @Slot(str, str)
    def send_halftone(self, algorithm, settings):
        settings_dict = json.loads(settings)
        self.writer.send_halftone(algorithm, settings_dict)

    @Slot(str)
    def send_colors(self, settings):
        settings_dict = json.loads(settings)
        self.writer.send_colors(settings_dict)

    @Slot(str)
    def open(self, path):
        path = QUrl(path).toLocalFile()
        self._paths["open_path"] = self.get_dir(path)
        self.writer.load_image(path)
        self.processingStarted.emit()

    @Slot()
    def open_clipboard(self):
        mime_data = self.clipboard.mimeData()
        if mime_data.hasImage():
            image = self.clipboard.image()
            self.processingStarted.emit()
            _image_np = qimage_to_numpy(image)
            # using pickle mostly for simplicity as I dont want to deal
            # with shared memory for an operation that happens so rarely.
            pickled_data = pickle.dumps(_image_np)
            self.writer.send_pickled_image(pickled_data)
        elif mime_data.hasUrls():
            url = mime_data.urls()[0]
            self.open_url(url)
            self.processingStarted.emit()
        elif mime_data.hasText():
            url = self.clipboard.text().strip().lower()
            if url.startswith("http://") or url.startswith("https://"):
                self.writer.send_url(url)
                self.processingStarted.emit()
            else:
                message = "Not a valid file location"
                self.showNotification.emit(message, 5000)
                self.loadFailed.emit()

        else:
            message = "No image data in clipboard"
            self.showNotification.emit(message, 5000)
            self.loadFailed.emit()

    @Slot(QUrl)
    def open_url(self, url):
        if url.isValid():
            if url.isLocalFile():
                path = url.toLocalFile()
                self._paths["open_path"] = self.get_dir(path)
                self.writer.send_url(url.toString(), local=url.isLocalFile())
            else:
                message = "Can't open remote file"
                self.showNotification.emit(message, 5000)
                self.loadFailed.emit()
        else:
            message = "Not a valid file location"
            self.showNotification.emit(message, 5000)
            self.loadFailed.emit()

    @Slot(str)
    def save(self, path):
        path = QUrl(path).toLocalFile()
        self._paths["save_path"] = self.get_dir(path)
        self.writer.save_image(path)
        # self.processingStarted.emit()

    @Slot()
    def save_to_clipboard(self):
        self.writer.save_to_clipboard()
        # self.processingStarted.emit()

    @Slot()
    def flip(self):
        self.writer.send_flip()
        if self._has_image:
            self.processingStarted.emit()

    @Slot(bool)
    def rotate(self, cw):
        self.writer.send_rotate(cw)
        if self._has_image:
            self.rotate_shm(cw)
            self.processingStarted.emit()

    @Slot()
    def invert(self):
        self.writer.send_invert()
        if self._has_image:
            self.processingStarted.emit()

    @Slot(bool)
    def save_like_preview(self, state):
        self.writer.save_like_preview(state)

    @Slot(bool)
    def save_ignore_alpha(self, state):
        self.writer.save_ignore_alpha(state)

    @Slot(bool)
    def toggle_native(self, state):
        config = get_config()
        config["window"]["native_frame"] = state
        save_config(config)

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
        self.image_provider.image = None
        if self.shm_preview is not None:
            del self.shm_preview
        if self.shm is not None:
            self.shm.close()

    def display_processed_image(self, array, reset=True):
        """Display the processed image in the photo viewer."""
        _img = np.ascontiguousarray(self.shm_preview)

        if array == "gray":
            pixmap = numpy_to_pixmap(_img[:, :, 0], qi=True)
        elif array == "rgb":
            pixmap = numpy_to_pixmap(_img, qi=True)

        self.image_provider.setImage(pixmap)
        self.displayImage.emit()
        if reset:
            self.resetView.emit()

        self.processing = False
        self._has_image = True

    def display_processed_image_nt(self, array, reset=True):
        """Display the processed image in the photo viewer on windows."""
        _img = pickle.loads(array)

        pixmap = numpy_to_pixmap(_img, qi=True)

        self.viewer.setImage(pixmap)
        if reset:
            self.resetView.emit()

        self.processing = False
        self._has_image = True

    def store_in_clipboard(self, data):
        image = pickle.loads(data)
        qimage = numpy_to_pixmap(image, qi=True)

        self.clipboard.setImage(qimage)

    def save_config(self):
        config = get_config()
        # window related
        config["window"]["x"] = int(self._window.property("x"))
        config["window"]["y"] = int(self._window.property("y"))
        config["window"]["width"] = int(self._window.property("width"))
        config["window"]["height"] = int(self._window.property("height"))
        config["window"]["maximized"] = int(self._window.property("maximized"))
        config["window"]["sidebar_width"] = int(self._window.property("sbw"))

        # theme related
        config["style"]["theme"] = int(self._window.property("themeIdx"))
        config["style"]["accent"] = int(self._window.property("accent"))

        # path related
        if self._paths["open_path"] is not None:
            config["paths"]["open_path"] = self._paths["open_path"]
        if self._paths["save_path"] is not None:
            config["paths"]["save_path"] = self._paths["save_path"]

        save_config(config)

    @staticmethod
    def get_dir(path):
        return os.path.dirname(path)

    def exit(self):
        # self.save_settings()
        self.save_config()
        self.image_provider.image = None
        self.close_shm()
        self.writer.close()
        self.daemon_process.join()
