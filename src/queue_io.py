from PySide6.QtCore import QObject, QTimer, Signal


class QueueReader(QObject):
    received_array = Signal(str, tuple)
    rotated = Signal(tuple)
    show_processing_label = Signal(bool)
    close_shm = Signal()
    received_processed = Signal(str, bool)
    received_processed_nt = Signal(bytes, bool)
    received_notification = Signal(str, int)
    grayscale_signal = Signal(bool)

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
            if message["type"] == "shared_array":
                name = message["name"]
                size = message["size"]
                self.received_array.emit(name, size)

            elif message["type"] == "close_shm":
                self.close_shm.emit()

            elif message["type"] == "display_image":
                array = message["array"]
                reset = message["reset"]
                self.received_processed.emit(array, reset)

            elif message["type"] == "display_image_nt":
                array = message["array"]
                reset = message["reset"]
                self.received_processed_nt.emit(array, reset)

            elif message["type"] == "data_for_clipboard":
                data = message["data"]
                self.window.store_in_clipboard(data)

            elif message["type"] == "started_processing":
                self.show_processing_label.emit(True)

            elif message["type"] == "notification":
                notification = message["notification"]
                duration = message["duration"]
                self.received_notification.emit(notification, duration)

            elif message["type"] == "enable_toolbox":
                state = message["state"]
                self.window.sidebar.toolbox.enable_buttons(state)

            elif message["type"] == "original_grayscale":
                value = message["value"]
                self.grayscale_signal.emit(value)


class QueueWriter(QObject):
    rotate = Signal(bool)

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

    def load_from_clipboard(self):
        message = {"type": "load_from_clipboard"}
        self.queue.put(message)
        self.window.display_processing_label(True)

    def send_pickled_image(self, pickled_data):
        message = {"type": "load_from_pickle", "data": pickled_data}
        self.queue.put(message)
        self.window.display_processing_label(True)

    def send_url(self, url):
        message = {"type": "load_from_url", "url": url}
        self.queue.put(message)

    def save_image(self):
        message = {"type": "save_image"}
        self.queue.put(message)

    def save_to_clipboard(self):
        message = {"type": "save_to_clipboard"}
        self.queue.put(message)

    def reset(self):
        message = {"type": "reset_storage"}
        self.queue.put(message)
        self.window.reset_viewer()

    def send_rotate(self, cw):
        message = {"type": "rotate", "cw": cw}
        self.queue.put(message)
        self.rotate.emit(cw)

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

    def ignore_alpha(self, value):
        message = {"type": "ignore_alpha", "value": value}
        self.queue.put(message)

    def send_halftone(self, algorithm, settings):
        message = {
            "type": "halftone_settings",
            "algorithm": algorithm,
            "settings": settings,
        }
        self.queue.put(message)

    def send_grayscale(self, mode, settings):
        message = {
            "type": "grayscale_settings",
            "mode": mode,
            "settings": settings,
        }
        self.queue.put(message)

    def send_enhance(self, settings):
        message = {
            "type": "enhance_settings",
            "settings": settings,
        }
        self.queue.put(message)
