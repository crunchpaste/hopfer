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
    size_signal = Signal(int, int, float)

    def __init__(self, queue, window=None, interval=50):
        super().__init__()
        self.queue = queue
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(interval)
        self.processing = False

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
                self.window.processing = False

            elif message["type"] == "display_image_nt":
                array = message["array"]
                reset = message["reset"]
                self.received_processed_nt.emit(array, reset)
                self.window.processing = False

            elif message["type"] == "data_for_clipboard":
                data = message["data"]
                self.window.store_in_clipboard(data)

            elif message["type"] == "started_processing":
                self.show_processing_label.emit(True)
                self.window.processing = True

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

            elif message["type"] == "update_paths":
                paths = message["paths"]
                self.window.paths = paths

            elif message["type"] == "image_size":
                w = message["width"]
                h = message["height"]
                self.window.h = h
                self.window.w = w


class QueueWriter(QObject):
    rotate = Signal(bool)

    def __init__(self, queue, window=None, interval=50):
        super().__init__()
        self.queue = queue
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_pending)
        self.timer.start(interval)

        # processing related
        self.pending = False
        self.g_settings = None
        self.g_mode = None
        self.e_settings = None
        self.h_settings = None
        self.h_algorithm = None

    def close(self):
        message = {"type": "exit"}
        self.queue.put(message)

    def update_paths(self, paths):
        message = {"type": "update_paths", "paths": paths}
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

    def resize(self, width, height, interpolation):
        message = {
            "type": "resize",
            "width": width,
            "height": height,
            "interpolation": interpolation,
        }
        self.queue.put(message)

    # TODO: Remove the dummy methods down there to make the class a bit cleaner.
    def send_grayscale(self, mode, settings):
        self.send_process("grayscale", settings, algorithm=mode)

    def send_enhance(self, settings):
        self.send_process("enhance", settings)

    def send_halftone(self, algorithm, settings):
        self.send_process("halftone", settings, algorithm)

    def send_process(self, type, settings, algorithm=None):
        self.pending = True
        if type == "grayscale":
            self.g_mode = algorithm
            self.g_settings = settings
        if type == "enhance":
            self.e_settings = settings
        if type == "halftone":
            self.h_algorithm = algorithm
            self.h_settings = settings

    def check_pending(self):
        if self.pending and not self.window.processing:
            message = {
                "type": "process",
                "g_mode": self.g_mode,
                "g_settings": self.g_settings,
                "e_settings": self.e_settings,
                "h_algorithm": self.h_algorithm,
                "h_settings": self.h_settings,
            }
            self.queue.put(message)

            # reset them all
            self.pending = False
            self.g_settings = None
            self.g_mode = None
            self.e_settings = None
            self.h_settings = None
            self.h_algorithm = None
        else:
            return
