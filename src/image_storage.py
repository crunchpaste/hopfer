import io
import json
import os
import pickle
from multiprocessing.managers import SharedMemoryManager
from urllib.parse import unquote, urlparse

import numpy as np
import requests
import SharedArray as sa
from PIL import Image, UnidentifiedImageError
from platformdirs import user_pictures_dir
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap

from helpers.image_conversion import numpy_to_pixmap
from helpers.paths import config_path

try:
    from algorithms.static import style_alpha, style_image
except ImportError:
    from algorithms.style_preview import style_alpha, style_image


class ImageStorage(QObject):
    """
    Class for managing the loading, processing, and saving of images.
    Handles original and processed images.
    """

    # Constants for image processing and saving
    MAX_SAVE_ATTEMPTS = 100
    NORMALIZED_MAX = 255.0

    # Captured by the ImageTab. It is used to disable the GrayscaleCombo.
    grayscale_signal = Signal(bool)

    def __init__(self, daemon):
        """
        Initialize the image storage with the main window context for notifications.

        :param main_window: The main window of the application, used for showing notifications.
        """
        super().__init__()
        # self.main_window = main_window

        self.daemon = daemon

        self.paths = self.daemon.paths

        self.res_queue = self.daemon.res_queue
        self.req_queue = self.daemon.req_queue

        self.smm = SharedMemoryManager()
        self.smm.start()
        self.shm = None

        self.shm_preview = None

        # Defaulting the paths to the user Pictures directory and
        # hopfer.png as the filename for saving if config is not found
        try:
            with open(config_path(), "r") as f:
                config = json.load(f)
                image_path = config["paths"]["open_path"]
                save_path = config["paths"]["save_path"]
        except Exception:
            image_path = user_pictures_dir()
            save_path = os.path.join(user_pictures_dir(), "hopfer.png")

        # self.image_path = image_path
        # self.save_path = save_path

        self.paths["image_path"] = image_path
        self.paths["save_path"] = save_path

        self.save_path_edited = False  # Track if the save path has been altered

        self.save_like_preview = False
        self.save_like_alpha = False

        self._original_image = None
        self.original_grayscale = False
        self._grayscale_image = None
        self._enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self._processed_image = None

        self.color_dark = np.array((34, 35, 35)).astype(np.uint8)
        self.color_light = np.array((240, 246, 246)).astype(np.uint8)
        self.color_alpha = np.array((250, 128, 114)).astype(np.uint8)

        self.reset_view = True
        self.algorithm = "None"

    def create_shm(self, height, width):
        if self.smm is not None:
            self.smm.shutdown()
        # self.smm = SharedMemoryManager()
        # self.smm.start()
        self.shm = self.smm.SharedMemory(size=height * width * 3)
        self.shm_preview = np.ndarray(
            (height, width, 3), dtype=np.uint8, buffer=self.shm.buf
        )
        message = {
            "type": "shared_array",
            "name": self.shm.name,
            "size": (height, width, 3),
        }
        self.res_queue.put(message)

    def create_shms(self, height, width):
        sa.delete("shm://gray")
        sa.delete("shm://rgb")
        # Create shared memory for the 2D grayscale array
        self.shm_preview = sa.create("shm://gray", (height, width), dtype=np.uint8)

        # Create shared memory for the 3D RGB array
        self.shm_rgb = sa.create("shm://rgb", (height, width, 3), dtype=np.uint8)
        message = {"type": "shared_arrays"}
        self.res_queue.put(message)

    def reset(self):
        # keeps the paths but discards all images
        # mostly there to make it easier to take screencaptures
        self._original_image = None
        self.original_grayscale = False
        self._grayscale_image = None
        self.enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None

        self.reset_view = True

        message = {"type": "enable_toolbox", "state": False}
        self.res_queue.put(message)

    def _load(self, image):
        # the final procedure of loading an image. expecs a pillow image.

        self.original_image, self.alpha = self.extract_alpha(image)
        h, w = self.original_image.shape[0], self.original_image.shape[1]

        try:
            self.create_shm(h, w)
        except Exception as e:
            print(f"CREATING SHM: {e}")

        # message = {type}

        message = {"type": "original_grayscale", "value": self.original_grayscale}

        self.res_queue.put(message)
        if self.original_grayscale:
            self.grayscale_image = self.original_image
        else:
            self.grayscale_image = None

        self.enhanced_image = None
        self.processed_image = None
        self.daemon.processor.reset = True

        try:
            self.daemon.processor.start(step=0)
        except Exception as e:
            print(e)

        message = {"type": "enable_toolbox", "state": True}
        self.res_queue.put(message)
        # self.main_window.sidebar.toolbox.enable_buttons()

    def load_image(self, image_path):
        """
        Load an image from a given path and convert it to grayscale (L mode).

        :param image_path: Path to the image file to load.
        """

        try:
            self.paths["image_path"] = image_path

            with open(config_path(), "r") as f:
                config = json.load(f)

            base_path = os.path.dirname(image_path)
            config["paths"]["open_path"] = base_path

            if (
                config["paths"]["open_path"] == config["paths"]["save_path"]
                and not self.save_path_edited
            ):
                # this should only happen if the user has not set a different folder
                # for saving this time, or the peviouslt in the config. I may be a
                # personal opinion but I quite prer havin independent input/output
                # folders.
                config["paths"]["save_path"] = os.path.join(base_path, "hopfer.png")

            else:
                #
                name_wo_ext = os.path.splitext(os.path.basename(image_path))[0]
                old_image = os.path.basename(self.paths["save_path"])
                self.paths["save_path"] = self.paths["save_path"].replace(
                    old_image, f"{name_wo_ext}.png"
                )

            with open(config_path(), "w") as f:
                json.dump(config, f, indent=2)

            pil_image = Image.open(image_path)

            self._load(pil_image)

        except (FileNotFoundError, UnidentifiedImageError) as e:
            self.show_notification(
                f"Error: Unable to open image.\n{e!s}", duration=10000
            )
        except Exception as e:
            self.show_notification(
                f"An unexpected error occurred: {e!s}", duration=10000
            )

    def load_from_pickle(self, data):
        buffer = pickle.loads(data)
        pil_image = Image.fromarray(buffer)
        pil_image = pil_image.convert("RGBA")
        self._load(pil_image)

    def load_from_url(self, url):
        if url != "":
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = io.BytesIO(response.content)
                    pil_image = Image.open(image_data)
                    self._load(pil_image)
                else:
                    self.show_notification(
                        f"Failed to retrieve image. Status code: {response.status_code}",
                        duration=10000,
                    )
                    return None
            except Exception as e:
                # if this fails it is captured by the load_image method
                print(f"Error: {e}")
                if url.startswith("file:///"):
                    parsed_url = urlparse(url)
                    local_path = unquote(parsed_url.path)
                    if os.name == "nt":
                        local_path = local_path.lstrip("/")
                    url = local_path
                self.load_image(url)
        else:
            self.show_notification("Error: No image data in clipboard.", duration=10000)

    @staticmethod
    def discard_alpha(alpha):
        # discard the alpha channel if its full of equal numbers
        # to save on furher processing.
        if np.all(alpha == alpha[0, 0]):
            return None
        else:
            return alpha

    def extract_alpha(self, image):
        if image.mode == "LA":
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float16)
            L = np_image[:, :, 0]
            A = self.discard_alpha(np_image[:, :, 1])

            self.original_grayscale = True
            return L, A
        elif image.mode == "L":
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float32)
            L = np_image
            A = None
            self.original_grayscale = True
            return L, A
        elif image.mode == "RGBA":
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float32)
            RGB = np_image[:, :, :3]
            A = self.discard_alpha(np_image[:, :, 3])
            RGB, is_gray = self.check_grayscale(RGB)
            self.original_grayscale = is_gray
            return RGB, A
        elif image.mode == "RGB":
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float32)
            RGB = np_image
            A = None
            RGB, is_gray = self.check_grayscale(RGB)
            self.original_grayscale = is_gray
            return RGB, A
        else:
            image = image.convert("RGB")
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float32)
            RGB = np_image
            RGB, is_gray = self.check_grayscale(RGB)
            A = None
            self.original_grayscale = is_gray
            return RGB, A

    def check_grayscale(self, rgb):
        """This is just a small function to check if an RGB image is actually grayscale. It saves time and resources on converting it to grayscale later on. Turns out using numpy's array_equal is much faster."""

        if np.array_equal(rgb[:, :, 0], rgb[:, :, 1]) and np.array_equal(
            rgb[:, :, 0], rgb[:, :, 2]
        ):
            r = np.copy(rgb[:, :, 0])
            return r, True
        else:
            return rgb, False

    def save_image(self):
        """
        Save the processed image to the disk. If the file already exists,
        it appends a counter to the filename to avoid overwriting.

        If the image is processed, save it, else, do nothing.
        """
        if self.processed_image is None:
            print("No processed image to save!")
            self.show_notification(
                "Oops! It seems like you haven't opened an image yet. Open an image and then you can save it.",
                duration=3000,
            )
            return

        save_path = self.paths["save_path"]

        if not save_path:
            # If there is no save path, and this happens when an image is pasted from
            # clipboard, save it to the user Pictures directory as hopfer.png and
            # set the Pictures directory as the save path so that the user can
            # find it if they miss the notification.
            base_path = user_pictures_dir()
            save_path = os.path.join(base_path, "hopfer.png")
            self.paths["save_path"] = save_path

        # only if the path was actually edited save it to the confing
        # so that next time it should be the default with a hopfer.png
        if self.save_path_edited:
            base_path = os.path.dirname(save_path)
            with open(config_path(), "r") as f:
                config = json.load(f)

            config["paths"]["save_path"] = os.path.join(base_path, "hopfer.png")

            with open(config_path(), "w") as f:
                json.dump(config, f, indent=2)

        base_path = os.path.dirname(save_path)
        base_name = os.path.basename(save_path)
        save_path = self.generate_unique_save_path(base_path, base_name)

        if self.save_like_preview and self.daemon.processor.algorithm != "None":
            image = style_image(self.processed_image, self.color_dark, self.color_light)
        else:
            image = (self.processed_image * 255).astype(np.uint8)

        # Convert processed image to PIL format and save
        if self.ignore_alpha or self.alpha is None:
            pil_image = Image.fromarray(image)
        else:
            alpha = (self.alpha * 255).astype(np.uint8)
            image_w_alpha = np.dstack((image, alpha))
            pil_image = Image.fromarray(image_w_alpha)

        try:
            pil_image.save(save_path)
        except Exception as e:
            self.show_notification(f"Error: {e}", duration=10000)

        self.show_notification(f"Image saved to {save_path}", duration=3000)
        print(f"Image saved to {save_path}")

    def save_to_clipboard(self):
        if self.processed_image is not None:
            clipboard = self.app.clipboard()
            styled = self.save_like_preview

            # TODO: I have to check how to create pixmaps directly from an array
            clipboard.setPixmap(
                self.get_processed_pixmap(compositing=False, styled=styled)
            )
            self.show_notification("Image stored in clipboard.")
        else:
            self.show_notification(
                "Image? What image? You haven't opened one yet.", duration=5000
            )

    def generate_unique_save_path(self, base_path, base_name):
        """
        Generate a unique save path for the image. If the file exists,
        a counter is appended to the base filename.

        :param base_path: The directory to save the image.
        :param base_name: The base name of the file (including extension).
        :return: A unique file path for saving.
        """
        # Extract the file extension (format) from the base_name
        base_name_without_ext = base_name.rsplit(".", 1)[0]
        file_format = "." + base_name.rsplit(".", 1)[1] if "." in base_name else ".png"

        counter = 1
        save_path = os.path.join(base_path, f"{base_name_without_ext}{file_format}")

        while os.path.exists(save_path) and counter < self.MAX_SAVE_ATTEMPTS:
            save_path = os.path.join(
                base_path, f"{base_name_without_ext}_{counter:03d}{file_format}"
            )
            counter += 1

        return save_path

    @staticmethod
    def f32(image):
        if image.dtype == np.float32:
            return image
        else:
            return image.astype(np.float32)

    @staticmethod
    def f16(image):
        if image.dtype == np.float16:
            return image
        else:
            return image.astype(np.float16)

    @staticmethod
    def b1(image):
        if image.dtype == np.bool:
            return image
        else:
            return image.astype(np.bool)

    @property
    def original_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        if self._original_image is not None:
            return self.f32(self._original_image)

    @original_image.setter
    def original_image(self, image):
        if image is not None:
            self._original_image = self.f16(image)

    @property
    def grayscale_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        if self._grayscale_image is not None:
            return self.f32(self._grayscale_image)

    @grayscale_image.setter
    def grayscale_image(self, image):
        if image is not None:
            self._grayscale_image = self.f16(image)

    @property
    def enhanced_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        if self._enhanced_image is not None:
            return self.f32(self._enhanced_image)
        return self.grayscale_image

    @enhanced_image.setter
    def enhanced_image(self, image):
        if image is not None:
            self._enhanced_image = self.f16(image)

    @property
    def processed_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        if self._processed_image is not None:
            if self.algorithm != "None":
                return self.b1(self._processed_image)
            else:
                return self._processed_image
        return self.enhanced_image

    @processed_image.setter
    def processed_image(self, image):
        if image is not None:
            if self.algorithm != "None":
                self._processed_image = self.b1(image)
            else:
                self._processed_image = self.f16(image)

    def get_original_pixmap(self):
        """
        Convert the original image to a QPixmap.

        :return: QPixmap of the original image.
        """
        return self._get_image_pixmap(self.original_image)

    def get_grayscale_pixmap(self):
        """
        Convert the grayscale image to a QPixmap.

        :return: QPixmap of the grayscale image.
        """

        return self._get_image_pixmap(self.grayscale_image)

    def get_processed_image(self):
        """
        Return the processed image.

        :return: Processed image array.
        """

        return self.processed_image

    def generate_processed_pixmap(self, compositing=True, styled=True):
        """
        Convert the processed image to a QPixmap. If no processed image exists,
        return the original pixmap.

        :return: QPixmap of the processed image (or original if not processed).
        """
        reset = self.reset_view
        if self.daemon.processor.algorithm == "None":
            # needed to avoid not C contiguous error
            _img = np.ascontiguousarray(self.processed_image)

            try:
                self.shm_preview[:, :, 0] = (_img * 255).astype(np.uint8)
            except Exception as e:
                print(f"GENERATING PIXMAPS: {e}")
            message = {"type": "display_image", "array": "gray", "reset": reset}
            self.res_queue.put(message)
            return
        else:
            if styled:
                color_dark = self.color_dark
                color_light = self.color_light
                color_alpha = self.color_alpha

                # return boolean_pixmap(self.processed_image, color_dark, color_light)

                if self.alpha is not None:
                    # alpha = np.copy(self.alpha) * 255
                    # result = np.dstack((themed_image, alpha.astype(np.uint8)))
                    if compositing:
                        result = style_alpha(
                            self.processed_image.astype(np.float32),
                            self.alpha,
                            color_dark,
                            color_light,
                            color_alpha,
                        )
                    else:
                        _img = style_image(
                            self.processed_image,
                            color_dark,
                            color_light,
                        )
                        alpha = (self.alpha * 255).astype(np.uint8)
                        result = np.dstack((_img, alpha))
                else:
                    result = style_image(self.processed_image, color_dark, color_light)
            else:
                _img = (self.processed_image * 255).astype(np.uint8)
                if self.alpha is not None:
                    alpha = (self.alpha * 255).astype(np.uint8)
                    result = np.dstack((_img, _img, _img, alpha))
                else:
                    result = _img

        self.shm_preview[:] = result
        message = {"type": "display_image", "array": "rgb", "reset": reset}
        self.res_queue.put(message)

    def _get_image_pixmap(self, image_array):
        """
        Helper method to convert an image array to QPixmap.

        :param image_array: Image in NumPy array format.
        :return: QPixmap object corresponding to the image array.
        """
        if image_array is not None:
            return numpy_to_pixmap(image_array)
        else:
            return QPixmap()  # Return an empty pixmap if image is None

    def set_processed_image(self, processed_image, reset):
        """
        Store the processed image.

        :param processed_image: Processed image as a NumPy array.
        """

        self.processed_image = processed_image

    def rotate_image(self, cw=True):
        if cw:
            self.original_image = np.rot90(self.original_image, k=-1)
            self.grayscale_image = np.rot90(self.grayscale_image, k=-1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=-1)
            self.processed_image = np.rot90(self.processed_image, k=-1)
            self.shm_preview = np.rot90(self.shm_preview, k=-1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=-1)
        else:
            self.original_image = np.rot90(self.original_image, k=1)
            self.grayscale_image = np.rot90(self.grayscale_image, k=1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=1)
            self.processed_image = np.rot90(self.processed_image, k=1)
            self.shm_preview = np.rot90(self.shm_preview, k=1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=1)

        # while this does not produce accurate results for the dithering
        # it is much faster than reprocessing the image on each transform.
        # the halftoning would be accurate again on the next reprocess.
        h, w = self.grayscale_image.shape
        self.reset_view = True

    def flip_image(self):
        self.original_image = np.fliplr(self.original_image)
        self.grayscale_image = np.fliplr(self.grayscale_image)
        self.enhanced_image = np.fliplr(self.enhanced_image)
        self.processed_image = np.fliplr(self.processed_image)
        if self.alpha is not None:
            self.alpha = np.fliplr(self.alpha)

        # while this does not produce accurate results for the dithering
        # it is much faster than reprocessing the image on each transform.
        # the halftoning would be accurate again on the next reprocess.

    def invert_image(self):
        self.original_image = 1 - self.original_image
        self.grayscale_image = 1 - self.grayscale_image
        self.enhanced_image = 1 - self.enhanced_image
        self.processed_image = 1 - self.processed_image

        # It may be a bit of a personal preference, but i don't believe
        # the view should be reset after inverting the colors.

    def show_notification(self, notification, duration=3000):
        """
        Show a notification in the main window's sidebar.

        :param message: The message to display.
        :param duration: Duration in milliseconds for how long the notification lasts.
        """
        message = {
            "type": "notification",
            "notification": notification,
            "duration": duration,
        }
        self.res_queue.put(message)
        # self.main_window.sidebar.notifications.show_notification(message, duration)
