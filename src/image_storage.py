import io
import os

import numpy as np
import requests
from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import QBuffer, QObject, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication  # used for clipboard management

from helpers.image_conversion import numpy_to_pixmap

try:
    from algorithms.static import style_image
except ImportError:
    from algorithms.style_preview import style_image


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
        self.image_path = None
        self.save_path = None
        self.original_image = None
        self.original_grayscale = False
        self.grayscale_image = None
        self.enhanced_image = None
        self.alpha = None
        self.ignore_alpha = False
        self.edited_image = None
        self.processed_image = None
        self.save_path_edited = False  # Track if the save path has been altered

    def _load(self, image):
        # the final procedure of loading an image. expecs a pillow image.

        self.original_image, self.alpha = self.extract_alpha(image)
        self.grayscale_signal.emit(self.original_grayscale)
        if self.original_grayscale:
            self.grayscale_image = self.original_image
        self.main_window.processor.reset = True
        self.main_window.processor.start()
        self.main_window.sidebar.toolbox.enable_save()

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
                self.load_image(_url)
        else:
            self.show_notification("Error: No image data in clipboard.", duration=10000)

    def extract_alpha(self, image):
        if image.mode == "LA":
            np_image = np.array(image) / self.NORMALIZED_MAX
            L = np_image[:, :, 0]
            A = np_image[:, :, 1]
            self.original_grayscale = True
            return L, A
        elif image.mode == "L":
            np_image = np.array(image) / self.NORMALIZED_MAX
            L = np_image
            A = None
            self.original_grayscale = True
            return L, A
        elif image.mode == "RGBA":
            np_image = np.array(image) / self.NORMALIZED_MAX
            RGB = np_image[:, :, :3]
            A = np_image[:, :, 3]
            RGB, is_gray = self.check_grayscale(RGB)
            self.original_grayscale = is_gray
            return RGB, A
        elif image.mode == "RGB":
            np_image = np.array(image) / self.NORMALIZED_MAX
            RGB = np_image
            A = None
            RGB, is_gray = self.check_grayscale(RGB)
            self.original_grayscale = is_gray
            return RGB, A
        else:
            image = image.convert("RGB")
            np_image = np.array(image) / self.NORMALIZED_MAX
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

        # Ensure the base name and directory are properly set
        if not self.save_path:
            print("No image path specified!")
            return

        base_dir = os.path.dirname(self.save_path)
        base_name = os.path.basename(self.save_path)
        save_path = self.generate_unique_save_path(base_dir, base_name)

        image = (self.processed_image * 255).astype(np.uint8)
        # Convert processed image to PIL format and save
        if self.ignore_alpha or self.alpha is None:
            pil_image = Image.fromarray(image)
        else:
            alpha = (self.alpha * 255).astype(np.uint8)
            image_w_alpha = np.dstack((image, alpha))
            pil_image = Image.fromarray(image_w_alpha)
        pil_image.save(save_path)

        self.show_notification(f"Image saved to {save_path}", duration=3000)
        print(f"Image saved to {save_path}")

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
            return self.grayscale_image

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

    def get_processed_pixmap(self):
        """
        Convert the processed image to a QPixmap. If no processed image exists,
        return the original pixmap.

        :return: QPixmap of the processed image (or original if not processed).
        """
        if self.main_window.processor.algorithm == "None":
            return (
                self._get_image_pixmap(self.processed_image)
                or self.get_original_pixmap()
            )
        else:
            color_dark = np.array((34, 35, 35)).astype(np.uint8)
            color_light = np.array((240, 246, 246)).astype(np.uint8)

            themed_image = style_image(self.processed_image, color_dark, color_light)

            if self.alpha is not None:
                alpha = np.copy(self.alpha) * 255
                result = np.dstack((themed_image, alpha.astype(np.uint8)))
            else:
                result = themed_image

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

    def show_notification(self, message, duration=3000):
        """
        Show a notification in the main window's sidebar.

        :param message: The message to display.
        :param duration: Duration in milliseconds for how long the notification lasts.
        """
        self.main_window.sidebar.notifications.show_notification(message, duration)
