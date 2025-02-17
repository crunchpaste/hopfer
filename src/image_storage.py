import io
import os
from urllib.parse import unquote, urlparse

import numpy as np
import requests
from PIL import Image, UnidentifiedImageError
from platformdirs import user_pictures_dir
from PySide6.QtCore import QBuffer, QObject, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication  # used for clipboard management

from helpers.image_conversion import numpy_to_pixmap

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

    # Result signal to update PhotoViewer captured by the main window
    result_signal = Signal(bool)
    # Captured by the ImageTab. It is used to disable the GrayscaleCombo.
    grayscale_signal = Signal(bool)

    def __init__(self, main_window):
        """
        Initialize the image storage with the main window context for notifications.

        :param main_window: The main window of the application, used for showing notifications.
        """
        super().__init__()
        self.app = QApplication.instance()
        self.main_window = main_window

        # Defaulting the paths to the user Pictures directory and
        # hopfer.png as the filename for saving
        self.image_path = user_pictures_dir()
        self.save_path = os.path.join(user_pictures_dir(), "hopfer.png")

        self.save_path_edited = False  # Track if the save path has been altered

        self.save_like_preview = False
        self.save_like_alpha = False

        self.original_image = None
        self.original_grayscale = False
        self.grayscale_image = None
        self.enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None

        self.color_dark = np.array((34, 35, 35)).astype(np.uint8)
        self.color_light = np.array((240, 246, 246)).astype(np.uint8)
        self.color_alpha = np.array((250, 128, 114)).astype(np.uint8)

    def reset(self):
        # keeps the paths but discards all images
        # mostly there to make it easier to take screencaptures
        self.original_image = None
        self.original_grayscale = False
        self.grayscale_image = None
        self.enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None

        self.main_window.reset_viewer()

    def _load(self, image):
        # the final procedure of loading an image. expecs a pillow image.

        self.original_image, self.alpha = self.extract_alpha(image)
        self.grayscale_signal.emit(self.original_grayscale)
        if self.original_grayscale:
            self.grayscale_image = self.original_image
        self.enhanced_image = self.grayscale_image
        self.processed_image = self.enhanced_image
        self.main_window.processor.reset = True
        self.main_window.processor.start()
        self.main_window.sidebar.toolbox.enable_buttons()

    def load_image(self, image_path):
        """
        Load an image from a given path and convert it to grayscale (L mode).

        :param image_path: Path to the image file to load.
        """
        try:
            self.image_path = image_path

            path_without_ext = image_path.rsplit(".", 1)[0]
            save_path = path_without_ext + ".png"
            self.save_path = save_path

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

    def load_from_clipboard(self):
        clipboard = self.app.clipboard()
        _image = clipboard.image()
        _url = clipboard.text()

        if not _image.isNull():
            # if there is any image data convert it to a pil image.
            # solution is mostly copied from: https://stackoverflow.com/questions/47289884/how-to-convert-qimageqpixmap-to-pil-image-in-python-3
            # seems to work perfectly well
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            _image.save(buffer, "PNG")
            pil_image = Image.open(io.BytesIO(buffer.data()))
            self._load(pil_image)

        elif _url != "":
            print(_url)
            try:
                response = requests.get(_url)
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
                print(e)
                if _url.startswith("file:///"):
                    parsed_url = urlparse(_url)
                    local_path = unquote(parsed_url.path)
                    if os.name == "nt":
                        local_path = local_path.lstrip("/")
                    _url = local_path
                self.load_image(_url)
        else:
            self.show_notification("Error: No image data in clipboard.", duration=10000)

    def extract_alpha(self, image):
        if image.mode == "LA":
            np_image = (np.array(image) / self.NORMALIZED_MAX).astype(np.float32)
            L = np_image[:, :, 0]
            A = np_image[:, :, 1]
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
            A = np_image[:, :, 3]
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

        if not self.save_path:
            # If there is no save path, and this happens when an image is pasted from
            # clipboard, save it to the user Pictures directory as hopfer.png and
            # set the Pictures directory as the save path so that the user can
            # find it if they miss the notification.
            base_dir = user_pictures_dir()
            save_path = os.path.join(base_dir, "hopfer.png")
            self.save_path = save_path

        base_dir = os.path.dirname(self.save_path)
        base_name = os.path.basename(self.save_path)
        save_path = self.generate_unique_save_path(base_dir, base_name)

        if self.save_like_preview and self.main_window.processor.algorithm != "None":
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

            # TODO: I have to check how to create pixmaps directly from an array
            clipboard.setPixmap(self.get_processed_pixmap(compositing=False))
            self.show_notification("Image stored in clipboard.")
        else:
            self.show_notification(
                "Image? What image? You haven't opened one yet.", duration=5000
            )

    def generate_unique_save_path(self, base_dir, base_name):
        """
        Generate a unique save path for the image. If the file exists,
        a counter is appended to the base filename.

        :param base_dir: The directory to save the image.
        :param base_name: The base name of the file (including extension).
        :return: A unique file path for saving.
        """
        # Extract the file extension (format) from the base_name
        base_name_without_ext = base_name.rsplit(".", 1)[0]
        file_format = "." + base_name.rsplit(".", 1)[1] if "." in base_name else ".png"

        counter = 1
        save_path = os.path.join(base_dir, f"{base_name_without_ext}{file_format}")

        while os.path.exists(save_path) and counter < self.MAX_SAVE_ATTEMPTS:
            save_path = os.path.join(
                base_dir, f"{base_name_without_ext}_{counter:03d}{file_format}"
            )
            counter += 1

        return save_path

    def get_original_image(self):
        """
        Return the original image as a NumPy array (normalized to [0, 1]).

        :return: Original image array.
        """
        return self.original_image

    def get_grayscale_image(self):
        """
        Return the grayscale image as a NumPy array (normalized to [0, 1]).

        :return: Grayscale image array.
        """
        return self.grayscale_image

    def get_enhanced_image(self):
        """
        Return the grayscale image as a NumPy array (normalized to [0, 1]).

        :return: Grayscale image array.
        """
        if self.enhanced_image is not None:
            return self.enhanced_image
        else:
            return self.get_grayscale_image()

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

    def get_processed_pixmap(self, compositing=True):
        """
        Convert the processed image to a QPixmap. If no processed image exists,
        return the original pixmap.

        :return: QPixmap of the processed image (or original if not processed).
        """
        if self.main_window.processor.algorithm == "None":
            # needed to avoid not C contiguous error
            _img = np.ascontiguousarray(self.processed_image)
            return self._get_image_pixmap(_img) or self.get_original_pixmap()
        else:
            color_dark = self.color_dark
            color_light = self.color_light
            color_alpha = self.color_alpha

            if self.alpha is not None:
                # alpha = np.copy(self.alpha) * 255
                # result = np.dstack((themed_image, alpha.astype(np.uint8)))
                if compositing:
                    result = style_alpha(
                        self.processed_image,
                        self.alpha,
                        color_dark,
                        color_light,
                        color_alpha,
                    )
                else:
                    _img = style_image(self.processed_image, color_dark, color_light)
                    alpha = (self.alpha * 255).astype(np.uint8)
                    result = np.dstack((_img, alpha))
            else:
                result = style_image(self.processed_image, color_dark, color_light)

            return self._get_image_pixmap(result) or self.get_original_pixmap()

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

        # Sending the signal to main_window
        self.result_signal.emit(reset)

    def rotate_image(self, cw=True):
        if cw:
            self.original_image = np.rot90(self.original_image, k=-1)
            self.grayscale_image = np.rot90(self.grayscale_image, k=-1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=-1)
            self.processed_image = np.rot90(self.processed_image, k=-1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=-1)
        else:
            self.original_image = np.rot90(self.original_image, k=1)
            self.grayscale_image = np.rot90(self.grayscale_image, k=1)
            self.enhanced_image = np.rot90(self.enhanced_image, k=1)
            self.processed_image = np.rot90(self.processed_image, k=1)
            if self.alpha is not None:
                self.alpha = np.rot90(self.alpha, k=1)

        # while this does not produce accurate results for the dithering
        # it is much faster than reprocessing the image on each transform.
        # the halftoning would be accurate again on the next reprocess.
        self.result_signal.emit(True)

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
        self.result_signal.emit(True)

    def invert_image(self):
        self.original_image = 1 - self.original_image
        self.grayscale_image = 1 - self.grayscale_image
        self.enhanced_image = 1 - self.enhanced_image
        self.processed_image = 1 - self.processed_image

        # It may be a bit of a personal preference, but i don't believe
        # the view should be reset after inverting the colors.
        self.result_signal.emit(False)

    def show_notification(self, message, duration=3000):
        """
        Show a notification in the main window's sidebar.

        :param message: The message to display.
        :param duration: Duration in milliseconds for how long the notification lasts.
        """
        self.main_window.sidebar.notifications.show_notification(message, duration)
