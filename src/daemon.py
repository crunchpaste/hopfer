import os

from setproctitle import setproctitle

from image_processor import ImageProcessor
from image_storage import ImageStorage


class Daemon:
    def __init__(self, response=None, request=None, paths=None):
        # this one is for returning to the GUI
        self.res_queue = response
        # this one is for taking instruction
        self.req_queue = request
        # for save and open directories
        self.paths = paths
        # shared memory manager
        self.smm = None

        # in case of linux, possibly mac too initialize here.
        if os.name != "nt":
            self.storage = ImageStorage(self)
            self.processor = ImageProcessor(self, self.storage)

    def run(self):
        # initializing processor and storage as windows uses spawn
        # instead of fork, and these classes cant be serialized
        if os.name == "nt":
            self.storage = ImageStorage(self)
            self.processor = ImageProcessor(self, self.storage)
        else:
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
                self.storage.load_from_url(url)
            elif message["type"] == "load_from_clipboard":
                # data = message["data"]
                self.storage.load_from_clipboard()
            elif message["type"] == "save_image":
                self.storage.save_image()
            elif message["type"] == "save_to_clipboard":
                self.storage.save_to_clipboard()
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
            elif message["type"] == "change_color":
                color = message["color"]
                if message["swatch"] == "dark":
                    self.storage.color_dark = color
                elif message["swatch"] == "light":
                    self.storage.color_light = color
                elif message["swatch"] == "alpha":
                    self.storage.color_alpha = color
                self.storage.generate_processed_pixmap()
            elif message["type"] == "save_like_preview":
                value = message["value"]
                self.storage.save_like_preview = value
            # PROCESSOR RELATED
            elif (
                message["type"] == "grayscale_settings"
                and self.storage.original_image is not None
            ):
                self.processor.grayscale_mode = message["mode"]
                self.processor.grayscale_settings = message["settings"]
                self.processor.convert = True
                self.processor.start(step=0)
            elif (
                message["type"] == "enhance_settings"
                and self.storage.original_image is not None
            ):
                self.processor.image_settings = message["settings"]
                self.processor.start(step=1)
            elif message["type"] == "halftone_settings":
                self.processor.algorithm = message["algorithm"]
                self.processor.settings = message["settings"]
                self.processor.start(step=2)

            elif message["type"] == "exit":
                del self.storage.shm_preview
                self.storage.smm.shutdown()
                break
