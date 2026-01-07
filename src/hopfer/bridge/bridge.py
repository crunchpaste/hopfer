import json
import logging
import os
import pickle
from multiprocessing import Process, Queue, shared_memory

import numpy as np
import platformdirs
from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication

from hopfer.core.daemon import Daemon
from hopfer.core.queue_io import QueueReader, QueueWriter
from hopfer.helpers.config import save_config
from hopfer.helpers.image_conversion import numpy_to_pixmap, qimage_to_numpy

# still not sure if i want to check available ram
# from psutil import virtual_memory

logger = logging.getLogger(__name__)


class Bridge(QObject):
    processingStarted = Signal()
    resetView = Signal()
    displayImage = Signal()
    removeImage = Signal()
    loadFailed = Signal()
    showNotification = Signal(str, int)
    originalGrayscale = Signal(bool)
    pathsChanged = Signal()
    hasImage = Signal()
    sizeChanged = Signal()

    def __init__(self, image_provider, config_obj, parent=None):
        super().__init__(parent)
        self.shm = None
        self.image_provider = image_provider
        self.config = config_obj
        self.processing = False
        self._has_image = False
        self._w = 0
        self._h = 0
        self._ratio = 1

        self._native_frame = self.config.window.native_frame

        self.clipboard = QGuiApplication.clipboard()
        self._initial_folder = platformdirs.user_videos_dir()

        self._window = None

        self._init_components()

    def _init_components(self):
        # the request queue
        self.req_queue = Queue()
        # the response queue
        self.res_queue = Queue()

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

    # You can call this like a method in Python,
    # but QML sees it as a property.
    @Property(int, notify=sizeChanged)
    def width(self):
        return self._w

    @Property(int, notify=sizeChanged)
    def height(self):
        return self._h

    @Property(float, notify=sizeChanged)
    def ratio(self):
        return self._ratio

    @Property(str)
    def initial_folder_url(self):
        return QUrl.fromLocalFile(self._initial_folder).toString()

    @Slot(str, str)
    def send_grayscale(self, algorithm, settings):
        settings_dict = json.loads(settings)
        self.writer.send_grayscale(algorithm, settings_dict)
        logger.debug("Sending grayscale signal to daemon")

    @Slot(str)
    def send_enhance(self, settings):
        settings_dict = json.loads(settings)
        self.writer.send_enhance(settings_dict)
        logger.debug("Sending enhance signal to daemon")

    @Slot(str, str)
    def send_halftone(self, algorithm, settings):
        settings_dict = json.loads(settings)
        self.writer.send_halftone(algorithm, settings_dict)
        logger.debug("Sending halftone signal to daemon")

    @Slot(int, int, str)
    def send_resize(self, w, h, interpolation):
        self.writer.resize(w, h, interpolation)
        logger.debug(f"Sending resize: {w}x{h} {interpolation}")

    @Slot(str)
    def send_colors(self, settings):
        settings_dict = json.loads(settings)
        self.writer.send_colors(settings_dict)
        logger.debug("Sending new colors to daemon")

    @Slot()
    def send_reset(self):
        self.writer.reset()
        self.removeImage.emit()
        logger.debug("Closing the image")

    @Slot(str)
    def open(self, path):
        path = QUrl(path).toLocalFile()
        logger.debug(f"Opening {path}")
        self._paths["open_path"] = self.get_dir(path)
        self.writer.load_image(path)
        self.processingStarted.emit()

    def open_path(self, path):
        logger.debug(f"Opening {path}")
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
        # this is done here as otherwise the ui would react live and break
        self._native_frame = state
        print(self._native_frame)

    # TODECIDE: not sure if i want to check the system memory and include a dependency. i'm leaving it like that for now.
    # @Slot(result=float)
    # def get_free_ram(self):
    #     # this one is mostly used to warn the user that memory getting low when resizing an image
    #     available = virtual_memory().available
    #     return available / (1024 * 1024)

    def init_array(self, name, size):
        self.shm = shared_memory.SharedMemory(name=name, track=False)
        self.shm_preview = np.frombuffer(dtype=np.uint8, buffer=self.shm.buf)

        expected_size = size[0] * size[1] * size[2]

        try:
            self.shm_preview = self.shm_preview[:expected_size].reshape(size)
        except ValueError as e:
            logger.debug(
                f"Reshape failed: {e}. Buffer size: {len(self.shm_preview)}, Needed: {expected_size}"
            )
            self.shm_preview = self.shm_preview.reshape(size)

    def rotate_shm(self, cw):
        if cw:
            self.shm_preview = np.rot90(self.shm_preview, k=-1)
        else:
            self.shm_preview = np.rot90(self.shm_preview, k=1)

    def close_shm(self):
        self.image_provider.setImage(None)
        if self.shm_preview is not None:
            del self.shm_preview
        if self.shm is not None:
            self.shm.close()
        logger.debug("Closed shared memory")

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

    def display_none(self):
        """Reset the image provider to none."""

        self.image_provider.setImage(None)
        self.displayImage.emit()

    def store_in_clipboard(self, data):
        image = pickle.loads(data)
        qimage = numpy_to_pixmap(image, qi=True)

        self.clipboard.setImage(qimage)

    def save_config(self):
        # on exit update the config, otherwise it would be overwriten
        self.config.window.native_frame = self._native_frame

        config = self.config.to_dict()

        # I guess this should work for now and would be slighly more reliable
        if self._paths["open_path"] is not None:
            path = os.path.normpath(self._paths["open_path"])
            config["paths"]["open_path"] = QUrl.fromLocalFile(path).toString()
        if self._paths["save_path"] is not None:
            path = os.path.normpath(self._paths["save_path"])
            config["paths"]["save_path"] = QUrl.fromLocalFile(path).toString()

        save_config(config)
        logger.debug("Saved config")

    @staticmethod
    def get_dir(path):
        return os.path.dirname(path)

    def exit(self):
        self.save_config()
        self.image_provider.setImage(None)
        self.close_shm()
        self.writer.close()
        self.daemon_process.join()
        logger.debug("Killed daemon")
