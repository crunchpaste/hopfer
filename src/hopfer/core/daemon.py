import os

from setproctitle import setproctitle

from hopfer.core.image_processor import ImageProcessor
from hopfer.core.image_storage import ImageStorage
from hopfer.helpers.hex_rgb import hex_to_numpy


class Daemon:
    def __init__(self, response=None, request=None, paths=None):
        # this one is for returning to the GUI
        self.res_queue = response
        # this one is for taking instruction
        self.req_queue = request
        # for save and open directories
        self.paths = paths

    def run(self):
        # initializing processor and storage as windows uses spawn
        # instead of fork, and these classes cant be serialized
        self.storage = ImageStorage(self)
        self.processor = ImageProcessor(self, self.storage)
        if os.name != "nt":
            # setproctitle seems to not work on windows too
            setproctitle("hopferd")
        while True:
            message = self.req_queue.get()
            # STORAGE RELATED
            if message["type"] == "load_image":
                path = message["path"]
                self.storage.load_image(path)
            elif message["type"] == "load_from_pickle":
                data = message["data"]
                self.storage.load_from_pickle(data)
            elif message["type"] == "load_from_url":
                url = message["url"]
                local = message["local"]
                self.storage.load_from_url(url, local)
            elif message["type"] == "load_from_clipboard":
                # data = message["data"]
                self.storage.load_from_clipboard()
            elif message["type"] == "resize":
                w = message["width"]
                h = message["height"]
                interpolation = message["interpolation"]
                self.storage.resize_original(w, h, interpolation)
            elif message["type"] == "save_image":
                path = message["path"]
                self.storage.save_image(path)
            elif message["type"] == "save_to_clipboard":
                self.storage.save_to_clipboard()
            elif message["type"] == "update_paths":
                paths = message["paths"]
                self.storage.paths = paths
            elif message["type"] == "reset_storage":
                self.storage.reset()
            elif message["type"] == "rotate":
                cw = message["cw"]
                self.storage.rotate_image(cw)
                self.storage.generate_processed_pixmap()
            elif message["type"] == "flip":
                self.storage.flip_image()
                self.storage.generate_processed_pixmap()
            elif message["type"] == "invert":
                self.storage.invert_image()
                self.storage.generate_processed_pixmap()
            elif message["type"] == "change_colors":
                dark = message["print"]
                light = message["paper"]
                alpha = message["alpha"]

                self.storage.color_dark = hex_to_numpy(dark)
                self.storage.color_light = hex_to_numpy(light)
                self.storage.color_alpha = hex_to_numpy(alpha)

                self.storage.reset_view = False

                self.storage.generate_processed_pixmap()
            elif message["type"] == "save_like_preview":
                value = message["value"]
                self.storage.save_like_preview = value
            elif message["type"] == "ignore_alpha":
                value = message["value"]
                self.storage.ignore_alpha = value

            # PROCESSOR RELATED
            elif message["type"] == "process":
                step = []
                if message["g_mode"] is not None:
                    self.processor.grayscale_mode = message["g_mode"]
                    self.processor.grayscale_settings = message["g_settings"]
                    self.processor.convert = True
                    step.append(0)
                if message["e_settings"] is not None:
                    self.processor.image_settings = message["e_settings"]
                    step.append(0)
                if message["h_algorithm"] is not None:
                    self.processor.algorithm = message["h_algorithm"]
                    self.processor.settings = message["h_settings"]
                    step.append(1)
                if self.storage.original_image is not None:
                    self.processor.start(step=min(step))

            elif message["type"] == "exit":
                del self.storage.shm_preview
                if self.storage.shm is not None:
                    self.storage.shm.close()
                    self.storage.shm.unlink()
                break
